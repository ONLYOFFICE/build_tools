exports.handlers = {
    processingComplete: function(e) {
        // array for filtered doclets
        let filteredDoclets = [];

        const cleanName = name => name ? name.replace('<anonymous>~', '').replaceAll('"', '') : name;

        const classesDocletsMap = {}; // doclets for classes write at the end
        let passedClasses = []; // passed classes for current editor

        // Remove dublicates doclets
        const latestDoclets = {};
        e.doclets.forEach(doclet => {
            const isMethod = doclet.kind === 'function' || doclet.kind === 'method';
            const hasTypeofEditorsTag = isMethod && doclet.tags && doclet.tags.some(tag => tag.title === 'typeofeditors' && tag.value.includes(process.env.EDITOR));

            const shouldAddMethod = 
                doclet.kind !== 'member' &&
                (!doclet.longname || doclet.longname.search('private') === -1) &&
                doclet.scope !== 'inner' && hasTypeofEditorsTag;

            if (shouldAddMethod || doclet.kind == 'typedef' || doclet.kind == 'class') {
                latestDoclets[doclet.longname] = doclet;
            }
        });
        e.doclets.splice(0, e.doclets.length, ...Object.values(latestDoclets));

        // check available classess for current editor
        for (let i = 0; i < e.doclets.length; i++) {
            const doclet = e.doclets[i];
            const isMethod = doclet.kind === 'function' || doclet.kind === 'method';
            const hasTypeofEditorsTag = isMethod && doclet.tags && doclet.tags.some(tag => tag.title === 'typeofeditors' && tag.value.includes(process.env.EDITOR));

            const shouldAdd = 
                doclet.kind !== 'member' &&
                (!doclet.longname || doclet.longname.search('private') === -1) &&
                doclet.scope !== 'inner' &&
                (!isMethod || hasTypeofEditorsTag);

            if (shouldAdd) {
                if (doclet.memberof && false == passedClasses.includes(cleanName(doclet.memberof))) {
                    passedClasses.push(cleanName(doclet.memberof));
                }
            }
            else if (doclet.kind == 'class') {
                classesDocletsMap[cleanName(doclet.name)] = doclet;
            }
        }

        // remove unavailave classes in current editor
        passedClasses = passedClasses.filter(className => {
            const doclet = classesDocletsMap[className];
            if (!doclet) {
                return true;
            }

            const hasTypeofEditorsTag = !!(doclet.tags && doclet.tags.some(tag => tag.title === 'typeofeditors'));

            // class is passes if there is no editor tag or the current editor is among the tags
            const isPassed = false == hasTypeofEditorsTag || doclet.tags.some(tag => tag.title === 'typeofeditors' && tag.value && tag.value.includes(process.env.EDITOR));
            return isPassed;
        });

        for (let i = 0; i < e.doclets.length; i++) {
            const doclet = e.doclets[i];
            const isMethod = doclet.kind === 'function' || doclet.kind === 'method';
            const hasTypeofEditorsTag = isMethod && doclet.tags && doclet.tags.some(tag => tag.title === 'typeofeditors' && tag.value.includes(process.env.EDITOR));

            const shouldAddMethod = 
                doclet.kind !== 'member' &&
                (!doclet.longname || doclet.longname.search('private') === -1) &&
                doclet.scope !== 'inner' && hasTypeofEditorsTag;

            if (shouldAddMethod) {
                // if the class is not in our map, then we deleted it ourselves -> not available in the editor
                if (false == passedClasses.includes(cleanName(doclet.memberof))) {
                    continue;
                }

                // We leave only the necessary fields
                doclet.memberof = cleanName(doclet.memberof);
                doclet.longname = cleanName(doclet.longname);
                doclet.name     = cleanName(doclet.name);

                // skip inherited methods if ovveriden in child class
                if (doclet.inherited && filteredDoclets.find((addedDoclet) => addedDoclet['name'] == doclet['name'] && addedDoclet['memberof'] == doclet['memberof'])) {
                    continue;
                }

                const filteredDoclet = {
                    comment:        doclet.comment,
                    description:    doclet.description,
                    memberof:       cleanName(doclet.memberof),

                    params: doclet.params ? doclet.params.map(param => ({
                        type: param.type ? {
                            names:      param.type.names,
                            parsedType: param.type.parsedType
                        } : param.type,

                        name:           param.name,
                        description:    param.description,
                        optional:       param.optional,
                        defaultvalue:   param.defaultvalue
                    })) : doclet.params,

                    returns: doclet.returns ? doclet.returns.map(returnObj => ({
                        type: {
                          names:        returnObj.type.names,
                          parsedType:   returnObj.type.parsedType
                        }
                    })) : doclet.returns,

                    name:           doclet.name,
                    longname:       cleanName(doclet.longname),
                    kind:           doclet.kind,
                    scope:          doclet.scope,

                    type: doclet.type ? {
                        names: doclet.type.names,
                        parsedType: doclet.type.parsedType
                    } : doclet.type,
                    
                    properties: doclet.properties ? doclet.properties.map(property => ({
                        type: property.type ? {
                            names:      property.type.names,
                            parsedType: property.type.parsedType
                        } : property.type,

                        name:           property.name,
                        description:    property.description,
                        optional:       property.optional,
                        defaultvalue:   property.defaultvalue
                    })) : doclet.properties,
                    
                    meta: doclet.meta ? {
                        lineno:   doclet.meta.lineno,
                        columnno: doclet.meta.columnno
                    } : doclet.meta,

                    see: doclet.see 
                };

                // Add the filtered doclet to the array
                filteredDoclets.push(filteredDoclet);
            }
            else if (doclet.kind == 'class') {
                // if the class is not in our map, then we deleted it ourselves -> not available in the editor
                if (false == passedClasses.includes(cleanName(doclet.name))) {
                    continue;
                }

                const filteredDoclet = {
                    comment:        doclet.comment,
                    description:    doclet.description,
                    name:           cleanName(doclet.name),
                    longname:       cleanName(doclet.longname),
                    kind:           doclet.kind,
                    scope:          "global",
                    augments:       doclet.augments || undefined,
                    meta: doclet.meta ? {
                        lineno:   doclet.meta.lineno,
                        columnno: doclet.meta.columnno
                    } : doclet.meta,
                    properties: doclet.properties ? doclet.properties.map(property => ({
                        type: property.type ? {
                            names:      property.type.names,
                            parsedType: property.type.parsedType
                        } : property.type,

                        name:           property.name,
                        description:    property.description,
                        optional:       property.optional,
                        defaultvalue:   property.defaultvalue
                    })) : doclet.properties,
                    see: doclet.see || undefined
                };
    
                filteredDoclets.push(filteredDoclet);
            }
            else if (doclet.kind == 'typedef') {
                const filteredDoclet = {
                    comment:        doclet.comment,
                    description:    doclet.description,
                    name:           cleanName(doclet.name),
                    longname:       cleanName(doclet.longname),
                    kind:           doclet.kind,
                    scope:          "global",

                    meta: doclet.meta ? {
                        lineno:   doclet.meta.lineno,
                        columnno: doclet.meta.columnno
                    } : doclet.meta,

                    properties: doclet.properties ? doclet.properties.map(property => ({
                        type: property.type ? {
                            names:      property.type.names,
                            parsedType: property.type.parsedType
                        } : property.type,

                        name:           property.name,
                        description:    property.description,
                        optional:       property.optional,
                        defaultvalue:   property.defaultvalue
                    })) : doclet.properties,

                    see: doclet.see,
                    type: doclet.type ? {
                        names: doclet.type.names,
                        parsedType: doclet.type.parsedType
                    } : doclet.type
                };

                filteredDoclets.push(filteredDoclet);
            }
        }

        // Replace doclets with a filtered array
        e.doclets.splice(0, e.doclets.length, ...filteredDoclets);
    }
};
