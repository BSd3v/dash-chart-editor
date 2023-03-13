# AUTO GENERATED FILE - DO NOT EDIT

export ''_customtransformaccordion

"""
    ''_customtransformaccordion(;kwargs...)
    ''_customtransformaccordion(children::Any;kwargs...)
    ''_customtransformaccordion(children_maker::Function;kwargs...)


A CustomTransformAccordion component.

Keyword arguments:
- `children` (a list of or a singular dash component, string or number; optional)
"""
function ''_customtransformaccordion(; kwargs...)
        available_props = Symbol[:children]
        wild_props = Symbol[]
        return Component("''_customtransformaccordion", "CustomTransformAccordion", "dash_chart_editor", available_props, wild_props; kwargs...)
end

''_customtransformaccordion(children::Any; kwargs...) = ''_customtransformaccordion(;kwargs..., children = children)
''_customtransformaccordion(children_maker::Function; kwargs...) = ''_customtransformaccordion(children_maker(); kwargs...)

