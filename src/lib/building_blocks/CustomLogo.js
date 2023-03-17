import PropTypes from 'prop-types';
import React, {Component} from 'react';

export default class CustomLogo extends Component {
    render() {
        return (
            <img
                className="sidebar__logo"
                src={this.props.src}
                style={this.props.style}
            />
        );
    }
}

CustomLogo.plotly_editor_traits = {sidebar_element: true};

CustomLogo.defaultProps = {
    style: {width: '100%', height: '50px', margin: '0px'},
};

CustomLogo.propTypes = {
    src: PropTypes.string,
    style: PropTypes.object,
};
