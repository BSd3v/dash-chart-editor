import React, {Component} from 'react';
import PropTypes from 'prop-types';
// import plotly from 'plotly.js/dist/plotly';
import PlotlyEditor from 'react-chart-editor';
import 'react-chart-editor/lib/react-chart-editor.css';
import ChartEditor from '../building_blocks/ChartEditor.react';
import {TRANSFORMABLE_TRACES} from 'react-chart-editor/lib/lib/constants';
import {omit} from 'ramda';
import {
    SPLIT_ALLOWED,
    traceTypes,
    categoryLayout,
} from '../building_blocks/extraVars';
import {chartCategory} from 'react-chart-editor/lib/lib/traceTypes';

class DashChartEditor extends Component {
    constructor(props) {
        super(props);
        this.gd = React.createRef();
        this.state = {
            data: [],
            layout: {},
            frames: [],
            context: {},
            traceTypesConfig: {
                complex: true,
            },
        };

        this.state.traceTypesConfig.traces = (_) =>
            traceTypes(_, chartCategory, this.props.traceOptions);
        this.state.traceTypesConfig.categories = (_) =>
            categoryLayout(
                _,
                chartCategory,
                this.state.traceTypesConfig.traces
            );

        this.updateOptions = this.updateOptions.bind(this);
    }

    loadFigure(figure) {
        this.updateOptions({
            data: figure.data,
            layout: figure.layout,
            frames: figure.frames,
        });
    }

    updateOptions = ({data, layout, frames}) => {
        data.map((d) => {
            if ('transforms' in d) {
                if (!TRANSFORMABLE_TRACES.includes(d.type)) {
                    const newTransforms = [];
                    d.transforms.map((t) => {
                        if (
                            t.type === 'filter' ||
                            (SPLIT_ALLOWED.includes(d.type) &&
                                t.type === 'groupby')
                        ) {
                            newTransforms.push(t);
                        }
                    });
                    if (newTransforms) {
                        d.transforms = newTransforms;
                    } else {
                        delete d.transforms;
                    }
                }
            }
        });
        let newFrames;
        if (frames) {
            newFrames = JSON.parse(JSON.stringify(frames));
        } else {
            newFrames = [];
        }
        if (layout.xaxis) {
            if (!('title' in layout.xaxis) && data[0].xsrc) {
                layout.xaxis.title = {text: data[0].xsrc};
            }
        }
        if (layout.yaxis) {
            if (!('title' in layout.yaxis) && data[0].ysrc) {
                layout.yaxis.title = {text: data[0].ysrc};
            }
        }
        const newData = JSON.parse(JSON.stringify(data));
        const newLayout = JSON.parse(JSON.stringify(layout));
        this.props.setProps({
            data: newData,
            layout: newLayout,
            frames: newFrames,
            figure: JSON.parse(
                JSON.stringify({
                    data: newData,
                    layout: newLayout,
                    frames: newFrames,
                })
            ),
        });
        this.setState({data, layout, frames});
    };

    render() {
        const {
            id,
            style,
            setProps,
            dataSources,
            loadFigure,
            config,
            ...restProps
        } = this.props;

        if (loadFigure) {
            this.loadFigure(loadFigure);
            setProps({loadFigure: null});
        }

        const dataSourceOptions = Object.keys(dataSources).map((name) => ({
            value: name,
            label: name,
        }));

        return (
            <div className="ploty-chart-editor" style={style} id={id}>
                <PlotlyEditor
                    ref={this.gd}
                    dataSources={dataSources}
                    dataSourceOptions={dataSourceOptions}
                    data={this.state.data}
                    layout={this.state.layout}
                    config={config}
                    frames={this.state.frames}
                    plotly={window.Plotly}
                    traceTypesConfig={this.state.traceTypesConfig}
                    onUpdate={(data, layout, frames) =>
                        this.updateOptions({data, layout, frames})
                    }
                    onRender={(data, layout, frames) =>
                        this.updateOptions({data, layout, frames})
                    }
                    useResizeHandler
                    debug
                    advancedTraceTypeSelector
                >
                    <ChartEditor
                        {...omit(
                            ['data', 'layout', 'frames', 'figure'],
                            restProps
                        )}
                    />
                </PlotlyEditor>
            </div>
        );
    }
}

export default DashChartEditor;

DashChartEditor.defaultProps = {
    config: {editable: true},
    styleOptions: true,
    structureOptions: true,
    annotateOptions: true,
    controlOptions: true,
    style: {width: '100%', height: '100%'},
};

DashChartEditor.propTypes = {
    /**
     * Dash prop to be registered for use with callbacks
     */
    id: PropTypes.string,

    /**
     * Input dataSources for driving the chart editors selections
     */
    dataSources: PropTypes.objectOf(PropTypes.array),

    /**
     * Output data of the chart editor
     */
    data: PropTypes.arrayOf(PropTypes.object),

    /**
     * Output layout of the chart editor
     */
    layout: PropTypes.object,

    /**
     * Output frames of the chart editor
     */
    frames: PropTypes.array,

    /**
     * Output figure of the chart editor (dcc.Graph esk output)
     */
    figure: PropTypes.exact({
        data: PropTypes.arrayOf(PropTypes.object),
        layout: PropTypes.object,
        frames: PropTypes.array,
    }),

    /**
     * style of the whole editing element, including charting area
     */
    style: PropTypes.object,

    /**
    children: PropTypes.any,
    */

    /**
     * Plotly config options, listed here: https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
     */
    config: PropTypes.object,

    /**
     * {data, layout, frames} given to the chart, used to populate selections and chart when loading
     */
    loadFigure: PropTypes.objectOf(PropTypes.any),

    /**
     * Logo that will be displayed in the chart editor
     */
    logoSrc: PropTypes.string,

    /**
     * Style object of the Logo
     */
    logoStyle: PropTypes.object,

    /**
     * Options that drive the available options under the "Structure" tree
     */
    structureOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            traces: PropTypes.bool,
            subplots: PropTypes.bool,
            transforms: PropTypes.bool,
        }),
    ]),

    /**
     * Options that drive the available options under the "Style" tree
     */
    styleOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            general: PropTypes.bool,
            traces: PropTypes.bool,
            axes: PropTypes.bool,
            maps: PropTypes.bool,
            legend: PropTypes.bool,
            colorBars: PropTypes.bool,
        }),
    ]),

    /**
     * Options that drive the available options under the "Annotate" tree
     */
    annotateOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            text: PropTypes.bool,
            shapes: PropTypes.bool,
            images: PropTypes.bool,
        }),
    ]),

    /**
     * Options that drive the available options under the "Control" tree
     */
    controlOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            sliders: PropTypes.bool,
            menus: PropTypes.bool,
        }),
    ]),

    /**
     * List of trace options to display
     */
    traceOptions: PropTypes.any,

    /**
     * Dash-assigned callback that gets fired when the input changes
     */
    setProps: PropTypes.func,
};
