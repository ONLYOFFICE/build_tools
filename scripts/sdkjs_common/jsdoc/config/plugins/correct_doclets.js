exports.handlers = {
    processingComplete: function(e) {
        const filteredDoclets = [];

        function checkNullProps(oDoclet) {
            for (let key of Object.keys(oDoclet)) {
                if (oDoclet[key] == null) {
                    delete oDoclet[key];
                }
                if (typeof(oDoclet[key]) == "object") {
                    checkNullProps(oDoclet[key]);
                }
            }
        }

        for (let i = 0; i < e.doclets.length; i++) {
            const doclet = e.doclets[i];
            if (true == doclet.undocumented || doclet.kind == 'package') {
                continue;
            }

            const filteredDoclet = {
                comment:        doclet.comment,

                meta: doclet.meta ? {
                    lineno:   doclet.meta.lineno,
                    columnno: doclet.meta.columnno
                } : doclet.meta,

                kind:           doclet.kind,
                since:          doclet.since,
                name:           doclet.name,
                type: doclet.type ? {
                    names: doclet.type.names,
                    parsedType: doclet.type.parsedType
                } : doclet.type,

                description:    doclet.description,
                memberof:       doclet.memberof,

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

                longname:       doclet.longname,
                scope:          doclet.scope,
                alias:          doclet.alias,

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
                see: doclet.see
            };

            checkNullProps(filteredDoclet)

            filteredDoclets.push(filteredDoclet);
        }

        e.doclets.splice(0, e.doclets.length, ...filteredDoclets);
    }
};