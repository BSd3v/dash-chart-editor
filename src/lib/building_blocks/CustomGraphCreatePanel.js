import React from 'react';
import PropTypes from 'prop-types';
import {
    Dropdown,
    DropdownCustom,
    Radio,
    PlotlySection,
    AxesCreator,
    SubplotCreator,
    TraceAccordion,
    TraceTypeSection,
    LocationSelector,
    Dropzone,
    Numeric,
} from 'react-chart-editor/lib/components';
import {
    HistogramInfoVertical,
    HistogramInfoHorizontal,
    Histogram2d,
} from 'react-chart-editor/lib/components/fields/derived';
import CustomDataSelector from './CustomDataSelector';
import CustomTraceSelector from './CustomTraceSelector';
import CustomDropdown from './CustomDropdown';

const CustomGraphCreatePanel = (props, {localize: _, setPanel}) => {
    const sum = (array) => array.reduce((a, b) => a + b, 0);
    const cnt = (array) => array.length;
    const average = (array) => sum(array) / cnt(array);
    /* eslint-disable */
    const calcAttribute = (e, props = {}) => {
        if (!props.container.value_agg) {
            props.updateContainer({
                value: cnt(props.container.valuesrc),
                value_agg: 'count',
            });
        } else {
            switch (props.container.value_agg) {
                case 'sum':
                    props.updateContainer({
                        value: sum(props.container.valuesrc),
                    });
                    break;
                case 'average':
                    props.updateContainer({
                        value: average(props.container.valuesrc),
                    });
                    break;
                default:
                    props.updateContainer({
                        value: cnt(props.container.valuesrc),
                    });
            }
        }
    };
    /* eslint-enable */
    return (
        <TraceAccordion
            canAdd
            traceFilterCondition={(t) =>
                !(
                    t.transforms &&
                    t.transforms.some((tr) =>
                        ['fit', 'moving-average'].includes(tr.type)
                    )
                )
            }
            canReorder
        >
            <CustomTraceSelector label={_('Type')} attr="type" show />

            <Dropzone attr="geojson" fileType="geojson" />
            <LocationSelector attr="type" />
            <CustomDataSelector label={_('Values')} attr="values" />
            <CustomDataSelector label={_('Labels')} attr="labels" />
            <CustomDataSelector label={_('Parents')} attr="parents" />
            <TraceTypeSection traceTypes={['sunburst', 'treemap']} mode="trace">
                <CustomDataSelector label={_('IDs')} attr="ids" />
            </TraceTypeSection>
            <TraceTypeSection traceTypes={['volume']} mode="trace">
                <CustomDataSelector label={_('Value')} attr="value" />
            </TraceTypeSection>
            <TraceTypeSection
                name={_('Image Options')}
                traceTypes={['image']}
                mode="trace"
            >
                <Dropzone attr="source" fileType="image" show />
                <Numeric label={_('Image Width')} attr="dx" clearable={false} />
                <Numeric
                    label={_('Image Height')}
                    attr="dy"
                    clearable={false}
                />
            </TraceTypeSection>
            <TraceTypeSection
                name={_('Indicator Options')}
                traceTypes={['indicator']}
                mode="trace"
            >
                <CustomDataSelector
                    label="Value Src"
                    attr="valuesrc"
                    onChange={calcAttribute}
                    show
                />
                <CustomDropdown
                    label={_('Value Src Aggregate')}
                    attr="value_agg"
                    options={[
                        {label: _('count'), value: 'count'},
                        {label: _('sum'), value: 'sum'},
                        {label: _('average'), value: 'average'},
                    ]}
                    clearable={false}
                    defaultOpt="count"
                    onChange={calcAttribute}
                    show
                />
                <Numeric
                    label={_('Value')}
                    attr="value"
                    clearable={false}
                    show
                />
                <DropdownCustom
                    label={_('Mode')}
                    attr="mode"
                    options={[
                        {label: _('number'), value: 'number'},
                        {label: _('delta'), value: 'delta'},
                        {label: _('number+delta'), value: 'number+delta'},
                        {
                            label: _('number+delta+gauge'),
                            value: 'number+delta+gauge',
                        },
                        {label: _('gauge'), value: 'gauge'},
                        {label: _('number+gauge'), value: 'number+gauge'},
                    ]}
                    clearable={false}
                />
                <Numeric
                    label={_('Delta Reference')}
                    attr="delta.reference"
                    clearable={true}
                />
                <DropdownCustom
                    label={_('Gauge Shape')}
                    attr="gauge.shape"
                    options={[
                        {label: _('angular'), value: 'angular'},
                        {label: _('bullet'), value: 'bullet'},
                    ]}
                    clearable={false}
                />
            </TraceTypeSection>
            <Dropdown
                label={_('Parent Value Mode')}
                attr="branchvalues"
                options={[
                    {label: _('Total'), value: 'total'},
                    {label: _('Remainder'), value: 'remainder'},
                ]}
                clearable={false}
            />
            <CustomDataSelector
                label={{
                    histogram2d: _('X Values'),
                    histogram: _('X Values'),
                    '*': _('X'),
                }}
                attr="x"
            />
            <CustomDataSelector
                label={{
                    histogram2d: _('Y Values'),
                    histogram: _('Y Values'),
                    '*': _('Y'),
                }}
                attr="y"
            />
            <CustomDataSelector
                label={{
                    choropleth: _('Values'),
                    histogram2d: _('Z Values'),
                    '*': _('Z'),
                }}
                attr="z"
            />
            <DropdownCustom
                label={_('GeoJSON Location Field')}
                attr="featureidkey"
                options={[
                    {label: _('id'), value: 'id'},
                    {label: _('Custom'), value: 'custom'},
                ]}
                customOpt="custom"
                dafaultOpt=""
                clearable={false}
            />
            <Numeric
                label={_('Radius')}
                attr="radius"
                min={0}
                max={50}
                showSlider
            />
            <CustomDataSelector label={_('Measure')} attr="measure" />
            <PlotlySection name={_('Nodes')}>
                <CustomDataSelector label={_('Labels')} attr="node.label" />
                <CustomDataSelector label={_('Groups')} attr="node.groups" />
                <CustomDataSelector label={_('X')} attr="node.x" />
                <CustomDataSelector label={_('Y')} attr="node.y" />
            </PlotlySection>
            <PlotlySection name={_('Links')}>
                <CustomDataSelector label={_('Sources')} attr="link.source" />
                <CustomDataSelector label={_('Targets')} attr="link.target" />
                <CustomDataSelector label={_('Values')} attr="link.value" />
                <CustomDataSelector label={_('Labels')} attr="link.label" />
            </PlotlySection>
            <Radio
                label={_('Orientation')}
                attr="orientation"
                options={[
                    {label: _('Vertical'), value: 'v'},
                    {label: _('Horizontal'), value: 'h'},
                ]}
            />
            <HistogramInfoVertical>
                {_(
                    'Note: in vertical orientation, X values are used for binning. If Y values are provided, they are used as inputs to the histogram function which you can configure in the '
                )}
                <a onClick={() => setPanel('Style', 'Traces')}>{_('Traces')}</a>
                {_(
                    ' panel under Style. If Y values are omitted, the histogram function defaults to Count.'
                )}
            </HistogramInfoVertical>
            <HistogramInfoHorizontal>
                {_(
                    'Note: in horizontal orientation, Y values are used for binning. If X values are provided, they are used as inputs to the histogram function which you can configure in the '
                )}
                <a onClick={() => setPanel('Style', 'Traces')}>{_('Traces')}</a>
                {_(
                    ' under Style panel. If X values are omitted, the histogram function defaults to Count.'
                )}
            </HistogramInfoHorizontal>
            <Histogram2d>
                {_(
                    'Note: X and Y Values are used for binning. If Z values are provided, they are used as inputs to the histogram function which you can configure in the '
                )}
                <a onClick={() => setPanel('Style', 'Traces')}>{_('Traces')}</a>
                {_(
                    ' under Style panel. If Z values are omitted, the histogram function defaults to Count.'
                )}
            </Histogram2d>
            <CustomDataSelector label={_('I (Optional)')} attr="i" />
            <CustomDataSelector label={_('J (Optional)')} attr="j" />
            <CustomDataSelector label={_('K (Optional)')} attr="k" />
            <CustomDataSelector label={_('Open')} attr="open" />
            <CustomDataSelector label={_('High')} attr="high" />
            <CustomDataSelector label={_('Low')} attr="low" />
            <CustomDataSelector label={_('Close')} attr="close" />
            <CustomDataSelector label={_('A')} attr="a" />
            <CustomDataSelector label={_('B')} attr="b" />
            <CustomDataSelector label={_('C')} attr="c" />
            <CustomDataSelector label={_('U')} attr="u" />
            <CustomDataSelector label={_('V')} attr="v" />
            <CustomDataSelector label={_('W')} attr="w" />
            <CustomDataSelector label={_('X start')} attr="starts.x" />
            <CustomDataSelector label={_('Y start')} attr="starts.y" />
            <CustomDataSelector label={_('Z start')} attr="starts.z" />
            <CustomDataSelector label={_('Headers')} attr="header.values" />
            <CustomDataSelector label={_('Columns')} attr="cells.values" />

            <TraceTypeSection
                traceTypes={['scatterpolar', 'scatterpolargl', 'barpolar']}
                mode="trace"
            >
                <CustomDataSelector label={_('Radius')} attr="r" />
                <CustomDataSelector label={_('Theta')} attr="theta" />
                <Dropdown
                    label={_('Theta Unit')}
                    options={[
                        {label: _('Radians'), value: 'radians'},
                        {label: _('Degrees'), value: 'degrees'},
                        {label: _('Gradians'), value: 'gradians'},
                    ]}
                    attr="thetaunit"
                    clearable={false}
                />
            </TraceTypeSection>
            <AxesCreator attr="fake_attr" />
            <SubplotCreator attr="fake_attr" />
            <PlotlySection name={_('Header Options')}>
                <CustomDataSelector
                    label={_('Fill Color')}
                    attr="header.fill.color"
                />
                <CustomDataSelector
                    label={_('Font Color')}
                    attr="header.font.color"
                />
                <CustomDataSelector
                    label={_('Font Size')}
                    attr="header.font.size"
                />
            </PlotlySection>
            <PlotlySection name={_('Cell Options')}>
                <CustomDataSelector
                    label={_('Fill Color')}
                    attr="cells.fill.color"
                />
                <CustomDataSelector
                    label={_('Font Color')}
                    attr="cells.font.color"
                />
                <CustomDataSelector
                    label={_('Font Size')}
                    attr="cells.font.size"
                />
            </PlotlySection>
            <PlotlySection name={_('Column Options')}>
                <CustomDataSelector label={_('Width')} attr="columnwidth" />
                <CustomDataSelector label={_('Order')} attr="columnorder" />
            </PlotlySection>
            <PlotlySection name={_('Options')}>
                <CustomDataSelector label={_('Intensity')} attr="intensity" />
                <CustomDataSelector label={_('Facecolor')} attr="facecolor" />
                <CustomDataSelector
                    label={_('Vertexcolor')}
                    attr="vertexcolor"
                />
                <Radio
                    label={_('Transpose')}
                    attr="transpose"
                    options={[
                        {label: _('No'), value: false},
                        {label: _('Yes'), value: true},
                    ]}
                />
            </PlotlySection>
        </TraceAccordion>
    );
};

export default CustomGraphCreatePanel;
CustomGraphCreatePanel.contextTypes = {
    localize: PropTypes.func,
    setPanel: PropTypes.func,
};
