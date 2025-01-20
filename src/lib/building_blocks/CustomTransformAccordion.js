import PropTypes from 'prop-types';
import React, {Component} from 'react';
import {
    connectTransformToTrace,
    PlotlyFold,
    PlotlyPanel,
} from 'react-chart-editor';
import {PanelMessage} from 'react-chart-editor/lib/components/containers/PanelEmpty';
import {TRANSFORMABLE_TRACES} from 'react-chart-editor/lib/lib/constants';
import {SPLIT_ALLOWED} from '../building_blocks/extraVars';

const TransformFold = connectTransformToTrace(PlotlyFold);

class CustomTransformAccordion extends Component {
    render() {
        const {
            fullContainer: {oldTransforms = []},
            localize: _,
            container,
            dataSourceOptions,
        } = this.context;
        const {children} = this.props;
        const transforms = container.transforms || oldTransforms

        const tempTransformTypes = [
            {label: _('Filter'), type: 'filter'},
            {label: _('Split'), type: 'groupby'},
            {label: _('Aggregate'), type: 'aggregate'},
            {label: _('Sort'), type: 'sort'},
        ];

        const transformTypes = [];

        console.log(transforms)

        tempTransformTypes.map((opt) => {
            if (
                TRANSFORMABLE_TRACES.includes(container.type) &&
                !(container.type === 'candlestick')
            ) {
                transformTypes.push(opt);
            } else if (
                opt.type === 'filter' ||
                (SPLIT_ALLOWED.includes(container.type) &&
                    opt.type === 'groupby') ||
                    opt.type === 'aggregate'
            ) {
                transformTypes.push(opt);
            }
        });

        const transformBy =
            container.transforms &&
            container.transforms.map((tr) => {
                let foldNameSuffix = '';
                if (tr.groupssrc) {
                    const groupssrc =
                        dataSourceOptions &&
                        dataSourceOptions.find((d) => d.value === tr.groupssrc);
                    foldNameSuffix = `: ${
                        groupssrc && groupssrc.label
                            ? groupssrc.label
                            : tr.groupssrc
                    }`;
                } else if (tr.targetsrc) {
                    const targetsrc =
                        dataSourceOptions &&
                        dataSourceOptions.find((d) => d.value === tr.targetsrc);
                    foldNameSuffix = `: ${
                        targetsrc && targetsrc.label
                            ? targetsrc.label
                            : tr.targetsrc
                    }`;
                }
                return foldNameSuffix;
            });

        const filteredTransforms = transforms.filter(({type}) => Boolean(type));
        const filteredChildren = [];
        children
            .filter((c) => c.props.label !== 'By')
            .map((c) => filteredChildren.push(c));
        const content =
            filteredTransforms.length &&
            filteredTransforms.map((tr, i) => (
                <TransformFold
                    key={i}
                    transformIndex={i}
                    name={`${
                        transformTypes.filter(({type}) => type === tr.type)[0]
                            .label
                    }${transformBy && transformBy[i]}`}
                    className={tr.type}
                    canDelete={true}
                >
                    {tr.type !== 'aggregate' ? children : filteredChildren}
                </TransformFold>
            ));

        // cannot have 2 Split transforms on one trace:
        // https://github.com/plotly/plotly.js/issues/1742
        const addActionOptions = [];
        transformTypes.map((opt) => {
            if (container.transforms) {
                if (
                    container.transforms.some((t) => t.type === 'groupby') &&
                    opt.type === 'groupby'
                ) {
                    //
                } else if (
                    container.transforms.some((t) => t.type === 'aggregate') &&
                    opt.type === 'aggregate'
                ) {
                    //
                } else if (
                    container.transforms.some((t) => t.type === 'sort') &&
                    opt.type === 'sort'
                ) {
                    //
                } else {
                    addActionOptions.push(opt);
                }
            } else {
                addActionOptions.push(opt);
            }
        });

        //      container.transforms && container.transforms.some((t) => t.type === 'groupby')
        //        ? transformTypes.filter((t) => t.type !== 'groupby')
        //        : transformTypes;

        const addAction = {
            label: _('Transform'),
            handler: addActionOptions.map(({label, type}) => {
                return {
                    label,
                    handler: (context) => {
                        const {fullContainer, updateContainer} = context;
                        if (updateContainer) {
                            const transformIndex = Array.isArray(
                                fullContainer.transforms
                            )
                                ? fullContainer.transforms.length
                                : 0;
                            if (!fullContainer.transforms) {fullContainer.transforms = []}
                            const key = `transforms[${transformIndex}]`;

                            const payload = {type};
                            if (type === 'filter') {
                                payload.target = [];
                                payload.targetsrc = null;
                                payload.value = ''
                                payload.operation = '!='
                            }
                            else if (type === 'groupby') {
                                payload.styles = [];
                                payload.groupssrc = null;
                                payload.groups = null;
                            }
                            else if (type === 'aggregate') {
                                payload.aggregations = [
                                    {target: 'y', enabled: true, func: 'first'}
                                ]
                            }
                            payload.enabled = true;
                            fullContainer.transforms[transformIndex] = payload
                            updateContainer({[key]: payload});
                        }
                    },
                };
            }),
        };

        return (
            <PlotlyPanel addAction={addAction}>
                {content ? (
                    content
                ) : (
                    <PanelMessage icon={null}>
                        <div style={{textAlign: 'left'}}>
                            <p>
                                <strong>{_('Filter')}</strong>{' '}
                                {_(
                                    ' transforms allow you to filter data out from a trace.'
                                )}
                            </p>
                            <p>
                                <strong>{_('Aggregate')}</strong>{' '}
                                {_(
                                    ' transforms allow you to summarize a trace using an aggregate function like "average" or "minimum".'
                                )}
                            </p>
                            {TRANSFORMABLE_TRACES.includes(container.type) &&
                                !(container.type === 'candlestick') && (
                                    <div>
                                        <p>
                                            <strong>{_('Split')}</strong>{' '}
                                            {_(
                                                ' transforms allow you to create multiple traces from one source trace, so as to style them differently.'
                                            )}
                                        </p>
                                        <p>
                                            <strong>{_('Sort')}</strong>{' '}
                                            {_(
                                                ' transforms allow you to sort a trace, so as to control marker overlay or line connection order.'
                                            )}
                                        </p>
                                    </div>
                                )}
                            {SPLIT_ALLOWED.includes(container.type) && (
                                <div>
                                    <p>
                                        <strong>{_('Split')}</strong>{' '}
                                        {_(
                                            ' transforms allow you to create multiple traces from one source trace, so as to style them differently.'
                                        )}
                                    </p>

                                </div>
                            )}
                        </div>
                        <p>
                            {_(
                                'Click on the + button above to add a transform.'
                            )}
                        </p>
                    </PanelMessage>
                )}
            </PlotlyPanel>
        );
    }
}

CustomTransformAccordion.contextTypes = {
    fullContainer: PropTypes.object,
    localize: PropTypes.func,
    container: PropTypes.object,
    dataSourceOptions: PropTypes.array,
};

CustomTransformAccordion.propTypes = {
    children: PropTypes.node,
};

export default CustomTransformAccordion;
