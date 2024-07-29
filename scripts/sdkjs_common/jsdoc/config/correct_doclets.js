exports.handlers = {
    processingComplete: function(e) {
        // Инициализация массива для сохранения отфильтрованных doclets
        let filteredDoclets = [];

        const cleanName = name => name ? name.replace('<anonymous>~', '').replaceAll('"', '') : name;

        const classesDocletsMap = {}; // доклеты классов пишем в конце
        let passedClasses = []; // те которые проходят для редактора

        // Убираем повторения оставляя посление doclets
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

        // набивка доступных классов текущего редактора
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

        // проходимся по классам и удаляем из мапы те, что недоступны в редакторе
        passedClasses = passedClasses.filter(className => {
            const doclet = classesDocletsMap[className];
            if (!doclet) {
                return true;
            }

            const hasTypeofEditorsTag = !!(doclet.tags && doclet.tags.some(tag => tag.title === 'typeofeditors'));

            // класс пропускаем если нет тега редактора или текущий редактор есть среди тегов 
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
                // если класса нет в нашей мапе, значит мы его удалили сами -> недоступен в редакторе
                if (false == passedClasses.includes(cleanName(doclet.memberof))) {
                    continue;
                }

                // Оставляем только нужные поля
                doclet.memberof = cleanName(doclet.memberof);
                doclet.longname = cleanName(doclet.longname);
                doclet.name     = cleanName(doclet.name);

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

                // Добавляем отфильтрованный doclet в массив
                filteredDoclets.push(filteredDoclet);
            }
            else if (doclet.kind == 'class') {
                // если класса нет в нашей мапе, значит мы его удалили сами -> недоступен в редакторе
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

        // Заменяем doclets на отфильтрованный массив
        e.doclets.splice(0, e.doclets.length, ...filteredDoclets);
    }
};
