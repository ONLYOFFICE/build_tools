source?=/build_tools/out
target=$(DESTDIR)
bintarget=$(target)/usr/bin
documentserversource=$(source)/linux_64/onlyoffice/documentserver
documentservertarget=$(target)/var/www/onlyoffice/documentserver
documentserver-examplesource=$(source)/linux_64/onlyoffice/documentserver-example
documentserver-exampletarget=$(target)/var/www/onlyoffice/documentserver-example
documentserveretcsource=$(source)/linux_64/onlyoffice/documentserver/server/Common/config
documentserveretctarget=$(target)/etc/onlyoffice/documentserver
documentserverexampleetcsource=$(source)/linux_64/onlyoffice/documentserver-example/config
documentserverexampleetctarget=$(target)/etc/onlyoffice/documentserver-example

documentserveretcnginxtarget=$(documentserveretctarget)/nginx
documentserveretcsupervisortarget=$(documentserveretctarget)/supervisor
documentserveretclogrotatetarget=$(documentserveretctarget)/logrotate
documentserverexampleetcnginxtarget=$(documentserverexampleetctarget)/nginx
documentserverexampleetcsupervisortarget=$(documentserverexampleetctarget)/supervisor

etclogrotatetarget=$(target)/etc/logrotate.d
etcnginxincludestarget=$(target)/etc/nginx/includes
etcsupervisorconfdtarget=$(target)/etc/supervisor/conf.d

documentservernpmtarget=$(documentservertarget)/npm

libtarget=$(target)/lib
liblink=/var/www/onlyoffice/documentserver/server/FileConverter/bin

#licensesource=$(source)/linux_64/onlyoffice/documentserver/server/license
#licensetarget=$(target)/var/www/onlyoffice/documentserver/license
# sdkjs-pluginssource=$(source)/linux_64/onlyoffice/documentserver/sdkjs-plugins
# sdkjs-pluginstarget=$(target)/var/www/onlyoffice/documentserver/sdkjs-plugins


all:
.PHONY	:	all

install:
	install -d $(bintarget)/
	install -d $(documentservertarget)/
	install -d $(documentserver-exampletarget)/
	install -d $(documentserveretctarget)/
	install -d $(documentserverexampleetctarget)/
	
	install -d $(documentserveretcnginxtarget)/
	install -d $(documentserveretcsupervisortarget)/
	install -d $(documentserveretclogrotatetarget)/
	install -d $(documentserverexampleetcnginxtarget)/
	install -d $(documentserverexampleetcsupervisortarget)/
	
	install -d $(documentservernpmtarget)/
	
	cp -a bin/* $(bintarget)/

	cp -a documentserver-nginx-conf/* $(documentserveretcnginxtarget)/
	cp -a documentserver-supervisor-conf/* $(documentserveretcsupervisortarget)/
	cp -a documentserver-logrotate-conf/* $(documentserveretclogrotatetarget)/
	cp -a documentserver-example-nginx-conf/* $(documentserverexampleetcnginxtarget)/
	cp -a documentserver-example-supervisor-conf/* $(documentserverexampleetcsupervisortarget)/

	cp -a $(documentserversource)/* $(documentservertarget)/
	install -d $(documentserver-exampletarget)/config/
	install -d $(documentserver-exampletarget)/welcome/
	cp -a documentserver-example-welcome/* $(documentserver-exampletarget)/welcome/
	install -m 755 $(documentserver-examplesource)/example $(documentserver-exampletarget)/

	cp -a $(documentserveretcsource)/* $(documentserveretctarget)/
	cp -a $(documentserverexampleetcsource)/* $(documentserverexampleetctarget)/

	$(MAKE) -C npm all
	
	install -m 644 npm/package.json $(documentservernpmtarget)/
	install -m 755 npm/json $(documentservernpmtarget)/

	install -d $(libtarget)/
	ln -s $(liblink)/libDjVuFile.so $(libtarget)/libDjVuFile.so
	ln -s $(liblink)/libdoctrenderer.so  $(libtarget)/libdoctrenderer.so
	ln -s $(liblink)/libEpubFile.so $(libtarget)/libEpubFile.so
	ln -s $(liblink)/libFb2File.so $(libtarget)/libFb2File.so
	ln -s $(liblink)/libgraphics.so $(libtarget)/libgraphics.so
	ln -s $(liblink)/libHtmlFile2.so $(libtarget)/libHtmlFile2.so
	ln -s $(liblink)/libHtmlRenderer.so $(libtarget)/libHtmlRenderer.so
	ln -s $(liblink)/libkernel.so $(libtarget)/libkernel.so
	ln -s $(liblink)/libPdfReader.so $(libtarget)/libPdfReader.so
	ln -s $(liblink)/libPdfWriter.so $(libtarget)/libPdfWriter.so
	ln -s $(liblink)/libUnicodeConverter.so $(libtarget)/libUnicodeConverter.so
	ln -s $(liblink)/libXpsFile.so $(libtarget)/libXpsFile.so
	ln -s $(liblink)/libicudata.so.58 $(libtarget)/libicudata.so.58
	ln -s $(liblink)/libicuuc.so.58 $(libtarget)/libicuuc.so.58

	install -d $(etclogrotatetarget)/
	ln -r -s $(documentserveretclogrotatetarget)/ds.conf $(etclogrotatetarget)/ds.conf

	install -d $(etcnginxincludestarget)/
	ln -r -s $(documentserveretcnginxtarget)/includes/ds-common.conf $(etcnginxincludestarget)/ds-common.conf
	ln -r -s $(documentserveretcnginxtarget)/includes/ds-docservice.conf $(etcnginxincludestarget)/ds-docservice.conf
	ln -r -s $(documentserverexampleetcnginxtarget)/includes/ds-example.conf $(etcnginxincludestarget)/ds-example.conf
	ln -r -s $(documentserveretcnginxtarget)/includes/ds-letsencrypt.conf $(etcnginxincludestarget)/ds-letsencrypt.conf
	ln -r -s $(documentserveretcnginxtarget)/includes/ds-spellchecker.conf $(etcnginxincludestarget)/ds-spellchecker.conf
	ln -r -s $(documentserveretcnginxtarget)/includes/http-common.conf $(etcnginxincludestarget)/http-common.conf

	install -d $(etcsupervisorconfdtarget)/
	ln -r -s $(documentserverexampleetcsupervisortarget)/ds.conf $(etcsupervisorconfdtarget)/ds.conf
	ln -r -s $(documentserveretcsupervisortarget)/ds-converter.conf $(etcsupervisorconfdtarget)/ds-converter.conf
	ln -r -s $(documentserveretcsupervisortarget)/ds-docservice.conf $(etcsupervisorconfdtarget)/ds-docservice.conf
	ln -r -s $(documentserverexampleetcsupervisortarget)/ds-example.conf $(etcsupervisorconfdtarget)/ds-example.conf
	ln -r -s $(documentserveretcsupervisortarget)/ds-metrics.conf $(etcsupervisorconfdtarget)/ds-metrics.conf




