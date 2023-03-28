% Auto-generated: do not edit by hand
\name{''DashChartEditor}

\alias{''DashChartEditor}

\title{DashChartEditor component}

\description{

}

\usage{
''DashChartEditor(id=NULL, annotateOptions=NULL, config=NULL,
controlOptions=NULL, dataSources=NULL, figure=NULL,
loadFigure=NULL, logoSrc=NULL, logoStyle=NULL,
saveState=NULL, structureOptions=NULL, style=NULL,
styleOptions=NULL, traceOptions=NULL)
}

\arguments{
\item{id}{Character. Dash prop to be registered for use with callbacks}

\item{annotateOptions}{Logical | lists containing elements 'text', 'shapes', 'images'.
those elements have the following types:
  - text (logical; optional)
  - shapes (logical; optional)
  - images (logical; optional). Options that drive the available options under the "Annotate" tree}

\item{config}{Named list. Plotly config options, listed here: https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js}

\item{controlOptions}{Logical | lists containing elements 'sliders', 'menus'.
those elements have the following types:
  - sliders (logical; optional)
  - menus (logical; optional). Options that drive the available options under the "Control" tree}

\item{dataSources}{List with named elements and values of type unnamed list. Input dataSources for driving the chart editors selections}

\item{figure}{Lists containing elements 'data', 'layout', 'frames'.
those elements have the following types:
  - data (list of named lists; optional): output data of the chart editor
  - layout (named list; optional): output layout of the chart editor
  - frames (unnamed list; optional): output frames of the chart editor. Output figure of the chart editor (dcc.Graph esk output)}

\item{loadFigure}{List with named elements and values of type logical | numeric | character | named list | unnamed list. {data, layout, frames} given to the chart, used to populate selections and chart when loading}

\item{logoSrc}{Character. Logo that will be displayed in the chart editor}

\item{logoStyle}{Named list. Style object of the Logo}

\item{saveState}{Logical. When passed True, this will save the current state of the grid to `figure`}

\item{structureOptions}{Logical | lists containing elements 'traces', 'subplots', 'transforms'.
those elements have the following types:
  - traces (logical; optional)
  - subplots (logical; optional)
  - transforms (logical; optional). Options that drive the available options under the "Structure" tree}

\item{style}{Named list. style of the whole editing element, including charting area}

\item{styleOptions}{Logical | lists containing elements 'general', 'traces', 'axes', 'maps', 'legend', 'colorbars'.
those elements have the following types:
  - general (logical; optional)
  - traces (logical; optional)
  - axes (logical; optional)
  - maps (logical; optional)
  - legend (logical; optional)
  - colorbars (logical; optional). Options that drive the available options under the "Style" tree}

\item{traceOptions}{Logical | numeric | character | named list | unnamed list. List of trace options to display}
}

\value{named list of JSON elements corresponding to React.js properties and their values}

