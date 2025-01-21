import React, {Component} from 'react';
import PropTypes from 'prop-types';
// import plotly from 'plotly.js/dist/plotly';
import PlotlyEditor from 'react-chart-editor';
import 'react-chart-editor/lib/react-chart-editor.css';
import ChartEditor from '../building_blocks/ChartEditor.react';
import '../building_blocks/chart-styling.css';
import {TRANSFORMABLE_TRACES} from 'react-chart-editor/lib/lib/constants';
import {omit} from 'ramda';
import {
    SPLIT_ALLOWED,
    traceTypes,
    categoryLayout,
} from '../building_blocks/extraVars';

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
            mounted: false,
        };

        this.state.traceTypesConfig.traces = (_) =>
            traceTypes(_, this.props.traceOptions);
        this.state.traceTypesConfig.categories = (_) =>
            categoryLayout(_, this.state.traceTypesConfig.traces);

        this.updateOptions = this.updateOptions.bind(this);
    }

    componentDidMount() {
        this.setState({mounted: true});
        if (this.props.loadFigure) {
            this.loadFigure(this.props.loadFigure, true);
        }
    }

    loadFigure(figure, bypass) {
        const {setProps} = this.props;
        // swap `filter_python` for `filter`
        figure.data.map((d) => {
            if (d.transforms) {  // Check if transforms exists
                d.transforms = d.transforms.map((t) => {
                    if (t.type === 'filter_python') {
                        t.type = 'filter';
                    }
                    return t;
                });
            }
            // adjusts if the filters dropped the data out, this keeps the chart editing properly
            if (d.x.length == 0) d.x = ['']
            if (d.y.length == 0) d.y = ['']
        });
        if (this.state.mounted || bypass) {
            this.updateOptions({
                data: figure.data,
                layout: figure.layout,
                frames: figure.frames,
            });
            setProps({loadFigure: null});
        }
    }

    saveState() {
        const {data, layout, frames} = this.state;
        let newFrames;
        if (frames) {
            newFrames = JSON.parse(JSON.stringify(frames));
        } else {
            newFrames = [];
        }
        const newData = JSON.parse(JSON.stringify(data));
        const newLayout = JSON.parse(JSON.stringify(layout));
        this.props.setProps({
            figure: {
                data: newData,
                layout: newLayout,
                frames: newFrames,
            },
            saveState: false,
        });
    }

    updateOptions = ({data, layout, frames}) => {
        data.map((d) => {
            if ('transforms' in d) {
                if (
                    !TRANSFORMABLE_TRACES.includes(d.type) ||
                    d.type === 'candlestick'
                ) {
                    const newTransforms = [];
                    d.transforms.map((t) => {
                        if (
                            t.type === 'filter' ||
                            (SPLIT_ALLOWED.includes(d.type) &&
                                t.type === 'groupby') || t.type == 'aggregate'
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
            if (d.type === 'image') {
                layout.yaxis.autorange = 'reversed';
            }
            if (['scattermap', 'scattermapbox'].includes(d.type)) {
                d['cluster'] = {
                    'enabled': false,
                    'maxzoom': 24
                }
            }
        });

        if (layout.xaxis) {
            if (!('title' in layout.xaxis) && data[0]?.xsrc) {
                layout.xaxis.title = {text: data[0].xsrc};
            }
        }
        if (layout.yaxis) {
            if (!('title' in layout.yaxis) && data[0]?.ysrc) {
                layout.yaxis.title = {text: data[0].ysrc};
            }
        }

        const setTitles = (info) => {
            if ('xaxis' in info) {
                if (layout['xaxis' + info.xaxis.split('x')[1]]) {
                    if (
                        !('title' in layout['xaxis' + info.xaxis.split('x')[1]])
                    ) {
                        layout['xaxis' + info.xaxis.split('x')[1]].title = {
                            text: info.xsrc,
                        };
                    }
                }
            }
            if ('yaxis' in info) {
                if (layout['yaxis' + info.yaxis.split('y')[1]]) {
                    if (
                        !('title' in layout['yaxis' + info.yaxis.split('y')[1]])
                    ) {
                        layout['yaxis' + info.yaxis.split('y')[1]].title = {
                            text: info.ysrc,
                        };
                    }
                }
            }
        };

        data.map(setTitles);

        this.setState({data, layout, frames});
        this.saveState()
    };

    render() {
        const {
            id,
            style,
            dataSources,
            loadFigure,
            saveState,
            config,
            ...restProps
        } = this.props;

        const dataSourceOptions = Object.keys(dataSources).map((name) => ({
            value: name,
            label: name,
        }));

        if (loadFigure) {
            this.loadFigure(loadFigure);
        }

        if (saveState) {
            this.saveState();
        }

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
    saveState: true,
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
     * Output figure of the chart editor (dcc.Graph esk output)
     */
    figure: PropTypes.exact({
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
     * When passed True, this will save the current state of the grid to `figure`
     */
    saveState: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the input changes
     */
    setProps: PropTypes.func,
};
