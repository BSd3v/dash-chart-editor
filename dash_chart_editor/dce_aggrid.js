
var dagfuncs = (window.dashAgGridFunctions = window.dashAgGridFunctions || {});
const {createElement, useState, useEffect, useRef, forwardRef} = React;

// Equivalent of _.omit in vanilla JS
function omit(obj, keys) {
    const result = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key) && !keys.includes(key)) {
            result[key] = obj[key];
        }
    }
    return result;
}

const AllComponentEditor = ({ value, ...params }, comp) => {
    const node = useRef(params.api.getRowNode(params.node.id));
    const newValue = useRef(value);
    const currentProps = useRef(null)


    const setProps = (propsToSet) => {
        if ('n_blur' in propsToSet) return
        if ('value' in propsToSet) {
            newValue.current = propsToSet.value;
        }
        currentProps.current = {...currentProps.current, ...propsToSet, setProps}
        setComponentProps({...currentProps.current, ...propsToSet, setProps})
    };

    if (comp.type == 'MultiSelect') {
        if (newValue.current && typeof newValue.current === 'string') {
            newValue.current = JSON.parse(newValue.current)
        }
    }
    comp['props'] = {
        ...omit(comp.props,
        ['array', 'api', 'cellStartedEdit', 'colDef',
        'column', 'columnApi', 'context', 'eGridCell', 'formatValue',
        'node', 'parseValue', 'rowIndex', 'stopEditing',
        'onKeyDown', 'eventKey']
        ),
        initiallyOpened: true,
        highlightToday: true,
        comboboxProps: {withinPortal: false, returnFocus: true,
        EventsTarget: {targetType: 'button'}},
        popoverProps: {withinPortal:false, returnFocus: true},
        onDropdownOpen: () => setProps({dropdownOpened: true}),
        onDropdownClose: () => setProps({dropdownOpened: false}),
        dropdownOpened: true,
    }

    if (params.colDef.cellEditorPopup) {
        comp['props']['style'] = { ...comp.props?.style, width: params.column.actualWidth - 2, zIndex: 2000 };
    }

    const [componentProps, setComponentProps] = useState(comp.props)

    const oldValue = value;
    const escaped = useRef(null);
    const editorRef = useRef(null);
    const [renderedComp, setRendererComp] = useState(null)

    const handleStop = ({ event, ...otherParams }) => {
        setTimeout(() => {
            if (!escaped.current) {
                if (comp.type == 'MultiSelect') {
                    if (newValue.current) {
                        newValue.current = JSON.stringify(newValue.current)
                    }
                }
                node.current.setDataValue(params.column.colId, newValue.current);
            }
        }, 1);
    };

    const handleKeyDown = (event) => {
        const {key} = event
        if (key == "Escape") {
            escaped.current = true;
        }
    };

    useEffect(() => {
        currentProps.current = comp.props
        params.api.addEventListener('cellEditingStopped', handleStop);
        document.addEventListener('keydown', handleKeyDown);
        params.colDef.suppressKeyboardEvent = (params) => {
            suppress = params.editing ? (params.event.key != 'Tab' && params.event.key != 'Escape') : false
            if (['Select', 'MultiSelect'].includes(comp.type) && suppress && params.event.key == 'Enter') {
                suppress = currentProps.current?.dropdownOpened
            }
            return suppress
        }
        return () => {
            setTimeout(() => {document.removeEventListener('keydown', handleKeyDown)
            delete params.colDef.suppressKeyboardEvent;
            params.api.removeEventListener('cellEditingStopped', handleStop);
            }, 1);
        };
    }, []);

    useEffect(() => {
        if (editorRef.current) {
            if (editorRef.current.querySelector('input')) {
                editorRef.current.querySelector('input').focus();
            } else {
                editorRef.current.focus()
            }
        }
    }, [renderedComp]);

    useEffect(() => {
            setRendererComp(
                createElement(
                    'div',
                    { ref: editorRef, tabIndex: 0 },
                    createElement(window[comp['namespace']][comp['type']], { ...currentProps.current, setProps})
                )
            )
        },
    [componentProps]);

    return renderedComp;
};

dagfuncs.AllComponentEditors = forwardRef((params, ref) => {
    const component = params.colDef.cellEditorParams.component;
    let componentForRender = component;

    if (component && component.props) {
        // Avoid mutating shared component props; create a shallow clone per invocation
        const componentProps = { ...component.props, value: params.value };
        componentForRender = { ...component, props: componentProps };
    }

    console.log('Rendering AllComponentEditor with params:', params, 'and componentForRender:', componentForRender);

    return AllComponentEditor(params, componentForRender);
});