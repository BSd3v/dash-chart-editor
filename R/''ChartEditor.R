# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''ChartEditor <- function(children=NULL, annotateOptions=NULL, controlOptions=NULL, logoSrc=NULL, logoStyle=NULL, menuPanelOrder=NULL, structureOptions=NULL, styleOptions=NULL) {
    
    props <- list(children=children, annotateOptions=annotateOptions, controlOptions=controlOptions, logoSrc=logoSrc, logoStyle=logoStyle, menuPanelOrder=menuPanelOrder, structureOptions=structureOptions, styleOptions=styleOptions)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'ChartEditor',
        namespace = 'dash_chart_editor',
        propNames = c('children', 'annotateOptions', 'controlOptions', 'logoSrc', 'logoStyle', 'menuPanelOrder', 'structureOptions', 'styleOptions'),
        package = 'dashChartEditor'
        )

    structure(component, class = c('dash_component', 'list'))
}
