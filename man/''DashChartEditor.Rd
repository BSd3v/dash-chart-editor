% Auto-generated: do not edit by hand
\name{''DashChartEditor}

\alias{''DashChartEditor}

\title{DashChartEditor component}

\description{

}

\usage{
''DashChartEditor(id=NULL, annotateOptions=NULL, config=NULL,
controlOptions=NULL, data=NULL, dataSources=NULL,
frames=NULL, layout=NULL, loadFigure=NULL, logoSrc=NULL,
logoStyle=NULL, structureOptions=NULL, style=NULL,
styleOptions=NULL)
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

\item{data}{Logical | numeric | character | named list | unnamed list. Output data of the chart editor}

\item{dataSources}{List with named elements and values of type unnamed list. Input dataSources for driving the chart editors selections}

\item{frames}{Logical | numeric | character | named list | unnamed list. Output frames of the chart editor}

\item{layout}{Logical | numeric | character | named list | unnamed list. Output layout of the chart editor}

\item{loadFigure}{List with named elements and values of type logical | numeric | character | named list | unnamed list. {data, layout, frames} given to the chart, used to populate selections and chart when loading}

\item{logoSrc}{Character. Logo that will be displayed in the chart editor}

\item{logoStyle}{Named list. Style object of the Logo}

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
}

\value{named list of JSON elements corresponding to React.js properties and their values}

