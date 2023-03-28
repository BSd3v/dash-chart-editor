
module DashChartEditor
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1a1"

include("jl/''_dashcharteditor.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dash_chart_editor",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "async-DashChartEditor.js",
    external_url = "https://unpkg.com/dash_chart_editor@0.0.1a1/dash_chart_editor/async-DashChartEditor.js",
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-DashChartEditor.js.map",
    external_url = "https://unpkg.com/dash_chart_editor@0.0.1a1/dash_chart_editor/async-DashChartEditor.js.map",
    dynamic = true,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_chart_editor.min.js",
    external_url = "https://unpkg.com/dash_chart_editor@0.0.1a1/dash_chart_editor/dash_chart_editor.min.js",
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_chart_editor.min.js.map",
    external_url = "https://unpkg.com/dash_chart_editor@0.0.1a1/dash_chart_editor/dash_chart_editor.min.js.map",
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
