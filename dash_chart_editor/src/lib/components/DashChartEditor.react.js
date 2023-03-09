import React, {Component} from 'react';
import PropTypes from 'prop-types';
//import plotly from 'plotly.js/dist/plotly';
import PlotlyEditor from 'react-chart-editor';
import 'react-chart-editor/lib/react-chart-editor.css';
import ChartEditor from "./ChartEditor.react"

const config = {editable: true};

class DashChartEditor extends Component {
  constructor(props) {
    super(props);
    this.gd = React.createRef();
    this.state = {
      data: [],
      layout: {},
      frames: [],
      context: {},
    };

    this.updateOptions = this.updateOptions.bind(this)
  }

  loadFigure(figure) {
    this.updateOptions({data: figure.data, layout: figure.layout, frames: figure.frames})
  }

  updateOptions = ({data, layout, frames}) => {
    this.props.setProps({
        data: JSON.parse(JSON.stringify(data)),
        layout: JSON.parse(JSON.stringify(layout)),
        frames: JSON.parse(JSON.stringify(frames)),
    })
    this.setState({data, layout, frames})
  }

  render() {
    const {
        id,
        data,
        layout,
        frames,
        targetid,
        style,
        setProps,
        dataSources,
        children,
        loadFigure
    } = this.props;

    if (loadFigure) {
        this.loadFigure(loadFigure)
        setProps({loadFigure: null})
    }

    const dataSourceOptions = Object.keys(dataSources).map(name => ({
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
          onUpdate={(data, layout, frames) => this.updateOptions({data, layout, frames})}
          onRender={(data, layout, frames) => this.updateOptions({data, layout, frames})}
          useResizeHandler
          debug
          advancedTraceTypeSelector
        >
            <ChartEditor />
        </PlotlyEditor>
      </div>
    );
  }
}

export default DashChartEditor;

DashChartEditor.propTypes = {
    id: PropTypes.string,
    data: PropTypes.any,
    dataSources: PropTypes.objectOf(PropTypes.array),
    layout: PropTypes.any,
    frames: PropTypes.any,
    style: PropTypes.object,
    children: PropTypes.any,
    loadFigure: PropTypes.objectOf(PropTypes.any)
}
