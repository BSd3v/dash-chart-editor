import DropdownWidget from 'react-chart-editor/lib/components/widgets/Dropdown';
import Field from 'react-chart-editor/lib/components/fields/Field';
import PropTypes from 'prop-types';
import React, {Component} from 'react';
import {connectToContainer} from 'react-chart-editor/lib/lib';
import {nestedTest} from './extraVars.js';

export class UnconnectedDropdown extends Component {
    render() {
        let placeholder;
        if (this.props.multiValued) {
            placeholder = this.props.fullValue;
        }
        const {options, container, attr, defaultOpt} = this.props;
        const value = container[attr] || defaultOpt;

        const style = nestedTest(this.props);

        return (
            <div style={style}>
                <Field {...this.props}>
                    <DropdownWidget
                        backgroundDark={this.props.backgroundDark}
                        options={options}
                        value={value}
                        onChange={(e) => {
                            this.props.updatePlot(e);
                            if (this.props.onChange) {
                                this.props.onChange(e, this.props);
                            }
                        }}
                        clearable={this.props.clearable}
                        placeholder={placeholder}
                        disabled={this.props.disabled}
                        components={this.props.components}
                    />
                </Field>
            </div>
        );
    }
}

UnconnectedDropdown.propTypes = {
    backgroundDark: PropTypes.bool,
    components: PropTypes.object,
    clearable: PropTypes.bool,
    fullValue: PropTypes.any,
    value: PropTypes.any,
    options: PropTypes.array.isRequired,
    updatePlot: PropTypes.func,
    disabled: PropTypes.bool,
    ...Field.propTypes,
};

UnconnectedDropdown.displayName = 'UnconnectedDropdown';

export default connectToContainer(UnconnectedDropdown);
