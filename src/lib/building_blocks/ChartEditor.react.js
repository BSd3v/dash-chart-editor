import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {PanelMenuWrapper} from 'react-chart-editor/lib/components';
import {
    StyleLayoutPanel,
    StyleAxesPanel,
    StyleMapsPanel,
    StyleLegendPanel,
    StyleNotesPanel,
    StyleShapesPanel,
    StyleSlidersPanel,
    StyleImagesPanel,
    StyleColorbarsPanel,
    StyleUpdateMenusPanel,
} from 'react-chart-editor/lib/default_panels';
import CustomGraphTransformsPanel from './CustomGraphTransformsPanel';
import CustomGraphCreatePanel from './CustomGraphCreatePanel';
import CustomStyleTracesPanel from './CustomStyleTracesPanel';
import {traceHasColorbar} from 'react-chart-editor/lib/default_panels/StyleColorbarsPanel';
import CustomLogo from './CustomLogo';
import {
    TRANSFORMABLE_TRACES,
    TRACE_TO_AXIS,
} from 'react-chart-editor/lib/lib/constants';
import CustomGraphSubplotsPanel from './CustomGraphSubplotsPanel';

class ChartEditor extends Component {
    constructor(props, context) {
        super(props, context);
        this.hasTransforms = this.hasTransforms.bind(this);
        this.hasAxes = this.hasAxes.bind(this);
        this.hasMenus = this.hasMenus.bind(this);
        this.hasSliders = this.hasSliders.bind(this);
        this.hasColorbars = this.hasColorbars.bind(this);
        this.hasLegend = this.hasLegend.bind(this);
    }

    hasTransforms() {
        return true
//        return this.context.fullData.some((d) =>
//            TRANSFORMABLE_TRACES.includes(d.type)
//        );
    }

    hasAxes() {
        return (
            Object.keys(this.context.fullLayout._subplots).filter(
                (type) =>
                    !['cartesian', 'mapbox'].includes(type) &&
                    this.context.fullLayout._subplots[type].length > 0
            ).length > 0
        );
    }

    hasMenus() {
        const {
            fullLayout: {updatemenus = []},
        } = this.context;

        return updatemenus.length > 0;
    }

    hasSliders() {
        const {
            layout: {sliders = []},
        } = this.context;

        return sliders.length > 0;
    }

    hasColorbars() {
        return this.context.fullData.some((d) => traceHasColorbar({}, d));
    }

    hasLegend() {
        return this.context.fullData.some((t) => t.showlegend !== undefined); // eslint-disable-line no-undefined
    }

    hasMaps() {
        return this.context.fullData.some((d) =>
            [...TRACE_TO_AXIS.geo, ...TRACE_TO_AXIS.mapbox].includes(d.type)
        );
    }

    buildPanels(obj, key, elem) {
        if (key in obj) {
            if (obj[key]) {
                return elem;
            }
        }
        return null;
    }

    buildStructure(_) {
        if (this.props.structureOptions) {
            const returning = [];
            if (this.props.structureOptions === true) {
                returning.push(
                    <CustomGraphCreatePanel
                        group={_('Structure')}
                        name={_('Traces')}
                        key={'traces'}
                    />
                );
                returning.push(
                    <CustomGraphSubplotsPanel
                        group={_('Structure')}
                        name={_('Subplots')}
                        key={'subplots'}
                    />
                );
                returning.push(
                    <CustomGraphTransformsPanel
                        group={_('Structure')}
                        name={_('Transforms')}
                        key={'transforms'}
                    />
                );
            } else {
                returning.push(
                    this.buildPanels(
                        this.props.structureOptions,
                        'traces',
                        <CustomGraphCreatePanel
                            group={_('Structure')}
                            name={_('Traces')}
                            key={'traces'}
                        />
                    )
                );
                returning.push(
                    this.buildPanels(
                        this.props.structureOptions,
                        'subplots',
                        <CustomGraphSubplotsPanel
                            group={_('Structure')}
                            name={_('Subplots')}
                            key={'subplots'}
                        />
                    )
                );
                returning.push(
                    this.buildPanels(
                        this.props.structureOptions,
                        'transforms',
                        <CustomGraphTransformsPanel
                            group={_('Structure')}
                            name={_('Transforms')}
                            key={'transforms'}
                        />
                    )
                );
            }
            return returning;
        }
        return null;
    }

    buildStyle(_) {
        if (this.props.styleOptions) {
            const returning = [];
            if (this.props.styleOptions === true) {
                returning.push(
                    <StyleLayoutPanel
                        group={_('Style')}
                        name={_('General')}
                        key={'general'}
                    />
                );
                returning.push(
                    <CustomStyleTracesPanel
                        group={_('Style')}
                        name={_('Traces')}
                        key={'traces_style'}
                    />
                );
                if (this.hasAxes()) {
                    returning.push(
                        <StyleAxesPanel
                            group={_('Style')}
                            name={_('Axes')}
                            key={'axes'}
                        />
                    );
                }
                if (this.hasMaps()) {
                    returning.push(
                        <StyleMapsPanel
                            group={_('Style')}
                            name={_('Maps')}
                            key={'maps'}
                        />
                    );
                }
                if (this.hasLegend()) {
                    returning.push(
                        <StyleLegendPanel
                            group={_('Style')}
                            name={_('Legend')}
                            key={'legend'}
                        />
                    );
                }
                if (this.hasColorbars()) {
                    returning.push(
                        <StyleColorbarsPanel
                            group={_('Style')}
                            name={_('Color Bars')}
                            key={'colorBars'}
                        />
                    );
                }
            } else {
                returning.push(
                    this.buildPanels(
                        this.props.styleOptions,
                        'general',
                        <StyleLayoutPanel
                            group={_('Style')}
                            name={_('General')}
                            key={'general'}
                        />
                    )
                );
                returning.push(
                    this.buildPanels(
                        this.props.styleOptions,
                        'traces',
                        <CustomStyleTracesPanel
                            group={_('Style')}
                            name={_('Traces')}
                            key={'traces_style'}
                        />
                    )
                );
                if (this.hasAxes()) {
                    returning.push(
                        this.buildPanels(
                            this.props.styleOptions,
                            'axes',
                            <StyleAxesPanel
                                group={_('Style')}
                                name={_('Axes')}
                                key={'axes'}
                            />
                        )
                    );
                }
                if (this.hasMaps()) {
                    returning.push(
                        this.buildPanels(
                            this.props.styleOptions,
                            'maps',
                            <StyleMapsPanel
                                group={_('Style')}
                                name={_('Maps')}
                                key={'maps'}
                            />
                        )
                    );
                }
                if (this.hasLegend()) {
                    returning.push(
                        this.buildPanels(
                            this.props.styleOptions,
                            'legend',
                            <StyleLegendPanel
                                group={_('Style')}
                                name={_('Legend')}
                                key={'legend'}
                            />
                        )
                    );
                }
                if (this.hasColorbars()) {
                    returning.push(
                        this.buildPanels(
                            this.props.styleOptions,
                            'colorBars',
                            <StyleColorbarsPanel
                                group={_('Style')}
                                name={_('Color Bars')}
                                key={'colorBars'}
                            />
                        )
                    );
                }
            }
            return returning;
        }
        return null;
    }

    buildAnnotations(_) {
        if (this.props.annotateOptions) {
            const returning = [];
            if (this.props.annotateOptions === true) {
                returning.push(
                    <StyleNotesPanel
                        group={_('Annotate')}
                        name={_('Text')}
                        key={'text'}
                    />
                );
                returning.push(
                    <StyleShapesPanel
                        group={_('Annotate')}
                        name={_('Shapes')}
                        key={'shapes'}
                    />
                );
                returning.push(
                    <StyleImagesPanel
                        group={_('Annotate')}
                        name={_('Images')}
                        key={'images'}
                    />
                );
            } else {
                returning.push(
                    this.buildPanels(
                        this.props.annotateOptions,
                        'text',
                        <StyleNotesPanel
                            group={_('Annotate')}
                            name={_('Text')}
                            key={'text'}
                        />
                    )
                );
                returning.push(
                    this.buildPanels(
                        this.props.annotateOptions,
                        'shapes',
                        <StyleShapesPanel
                            group={_('Annotate')}
                            name={_('Shapes')}
                            key={'shapes'}
                        />
                    )
                );
                returning.push(
                    this.buildPanels(
                        this.props.annotateOptions,
                        'images',
                        <StyleImagesPanel
                            group={_('Annotate')}
                            name={_('Images')}
                            key={'images'}
                        />
                    )
                );
            }
            return returning;
        }
        return null;
    }

    buildControls(_) {
        if (this.hasSliders() || this.hasMenus()) {
            const returning = [];
            if (this.props.controlOptions) {
                if (this.props.controlOptions === true) {
                    if (this.hasSliders()) {
                        returning.push(
                            <StyleSlidersPanel
                                group={_('Control')}
                                name={_('Sliders')}
                                key={'sliders'}
                            />
                        );
                    }
                    if (this.hasMenus()) {
                        returning.push(
                            <StyleUpdateMenusPanel
                                group={_('Control')}
                                name={_('Menus')}
                                key={'menus'}
                            />
                        );
                    }
                } else {
                    if (this.hasSliders()) {
                        returning.push(
                            this.buildPanels(
                                this.props.controlOptions,
                                'sliders',
                                <StyleSlidersPanel
                                    group={_('Control')}
                                    name={_('Sliders')}
                                    key={'sliders'}
                                />
                            )
                        );
                    }
                    if (this.hasMenus()) {
                        returning.push(
                            this.buildPanels(
                                this.props.controlOptions,
                                'menus',
                                <StyleUpdateMenusPanel
                                    group={_('Control')}
                                    name={_('Menus')}
                                    key={'menus'}
                                />
                            )
                        );
                    }
                }
                return returning;
            }
        }
        return null;
    }

    render() {
        const _ = this.context.localize;
        const logo = this.props.logoSrc && (
            <CustomLogo src={this.props.logoSrc} style={this.props.logoStyle} />
        );
        const structure = this.buildStructure(_);
        const styles = this.buildStyle(_);
        const annotate = this.buildAnnotations(_);
        const controls = this.buildControls(_);

        return (
            <PanelMenuWrapper menuPanelOrder={this.props.menuPanelOrder}>
                {logo ? logo : null}
                {structure}
                {styles}
                {annotate}
                {controls}
                {this.props.children ? this.props.children : null}
            </PanelMenuWrapper>
        );
    }
}

ChartEditor.propTypes = {
    children: PropTypes.node,
    logoSrc: PropTypes.string,
    logoStyle: PropTypes.object,
    menuPanelOrder: PropTypes.array,
    structureOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            traces: PropTypes.bool,
            subplots: PropTypes.bool,
            transforms: PropTypes.bool,
        }),
    ]),
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
    annotateOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            text: PropTypes.bool,
            shapes: PropTypes.bool,
            images: PropTypes.bool,
        }),
    ]),
    controlOptions: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.shape({
            sliders: PropTypes.bool,
            menus: PropTypes.bool,
        }),
    ]),
};

ChartEditor.contextTypes = {
    localize: PropTypes.func,
    fullData: PropTypes.array,
    fullLayout: PropTypes.object,
    layout: PropTypes.object,
};

export default ChartEditor;
