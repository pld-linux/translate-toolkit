#
# Conditional build:
%bcond_with	apidocs		# do not package API docs
%bcond_with	doc			# do not package user docs

Summary:	Tools to assist with translation and software localization
Name:		translate-toolkit
Version:	2.1.0
Release:	1
License:	GPL v2+
Group:		Development/Tools
Source0:	https://github.com/translate/translate/releases/download/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	302d20ad12a34da9992ef14f4ba13261
Patch0:		%{name}-stoplist.patch
Patch1:		%{name}-langmodel_dir.patch
Patch2:		unbash.patch
URL:		http://toolkit.translatehouse.org/
BuildRequires:	checkbashisms
BuildRequires:	python-dateutil
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
BuildRequires:	sed >= 4.0
%if %{with doc}
BuildRequires:	python-lxml
BuildRequires:	python-simplejson
BuildRequires:	python-vobject
%endif
Requires:	python-iniparse >= 0.3.1
Requires:	python-lxml >= 2.1.0
Requires:	python-modules >= 1:2.7
Requires:	python-setuptools
Requires:	python-simplejson
Requires:	python-vobject >= 0.6.6
%ifarch %{ix86}
Requires:	python-psyco
%endif
Suggests:	iso-codes
Suggests:	python-Levenshtein >= 0.10.2
Suggests:	python-pyenchant
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A set of tools for managing translation and software localization via
Gettext PO or XLIFF format files.

Including:
- Convertors: convert from various formats to PO or XLIFF
- Formats:
  - Core localization formats - XLIFF and Gettext PO
  - Other localization formats - TMX, TBX, Qt Linguist (.ts), Java
    .properties, Wordfast TM, OmegaT glossary
  - Compiled formats: Gettext MO, Qt .qm
  - Other formats - OpenDocument Format (ODF), text, HTML, CSV, INI,
    wiki (MediaWiki, DokuWiki), iCal
  - Specialised - OpenOffice.org GSI/SDF, PHP, Mozilla (.dtd,
    .properties, etc), Symbian, Innosetup, tikiwiki, subtitles
- Tools: count, search, debug, segment and pretranslate localization
  files. Extract terminology. Pseudo-localize
- Checkers: validate translations with over 45 checks

%package apidocs
Summary:	Development API for translate-toolkit applications
Group:		Documentation

%description apidocs
Translate Toolkit API documentation for developers wishing to build
new tools for the toolkit or to use the libraries in other
localization tools.

%package doc
Summary:	User Manual for translate-toolkit
Group:		Documentation

%description doc
Documentation for translate-toolkit.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

# FIXME: they do it wrong apparently? that can't do via setup.py?
%{__sed} -i -e 's#packagesdir = get_python_lib()#packagesdir = "%{py_sitescriptdir}"#' setup.py

%build
checkbashisms $(grep -rl '#!/bin/sh' tools)

%py_build

rm -r docs/_build/html/_sources

%if %{with doc}
# create manpages
install -d man
for script in build-2/scripts-%{py_ver}/*; do
	program=${script##*/}

	# exclude some known failures
	case $program in
		build_firefox.sh|\
		build_tmdb|\
		buildxpi.py|\
		get_moz_enUS.py|\
		junitmsgfmt|\
		pocommentclean|\
		pocompendium|\
		pocount|\
		pomigrate2|\
		popuretext|\
		poreencode|\
		posplit|\
		tmserver|\
		...)
		continue
		;;
	esac

	LC_ALL=C PYTHONPATH=. $script --manpage > man/$program.1
	# if this grep fails, you should exclude it above
	grep 'Autogenerated manpage' man/$program.1
done
%endif

%install
rm -rf $RPM_BUILD_ROOT
%py_install
%py_postclean

%if %{with doc}
install -d $RPM_BUILD_ROOT%{_mandir}/man1
cp -a man/* $RPM_BUILD_ROOT%{_mandir}/man1
%endif

# remove documentation files from site-packages
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/docs
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/{COPYING,README.rst}

# Move data files to %{_datadir}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/share/* $RPM_BUILD_ROOT%{_datadir}/%{name}

# we don't package tests
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/tools/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/convert/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/filters/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/lang/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/misc/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/search/indexing/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/search/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/placeables/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/xml_extract/test_*.py*

# build lang file
echo "%dir %{py_sitescriptdir}/translate/lang" > %{name}.lang
for a in $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/lang/*.py[co]; do
	# path file and lang
	p=${a#$RPM_BUILD_ROOT} f=${a##*/} l=${f%.py*}
	case $l in
	code_or|common|data|factory|identify|__init__|ngram|poedit)
		echo $p >> %{name}.lang
		;;
	*)
		echo "%lang($l) $p" >> %{name}.lang
		;;
	esac
done

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README.rst
%attr(755,root,root) %{_bindir}/build_firefox.sh
%attr(755,root,root) %{_bindir}/build_tmdb
%attr(755,root,root) %{_bindir}/buildxpi.py
%attr(755,root,root) %{_bindir}/csv2po
%attr(755,root,root) %{_bindir}/csv2tbx
%attr(755,root,root) %{_bindir}/get_moz_enUS.py
%attr(755,root,root) %{_bindir}/html2po
%attr(755,root,root) %{_bindir}/ical2po
%attr(755,root,root) %{_bindir}/idml2po
%attr(755,root,root) %{_bindir}/ini2po
%attr(755,root,root) %{_bindir}/json2po
%attr(755,root,root) %{_bindir}/junitmsgfmt
%attr(755,root,root) %{_bindir}/moz2po
%attr(755,root,root) %{_bindir}/mozlang2po
%attr(755,root,root) %{_bindir}/odf2xliff
%attr(755,root,root) %{_bindir}/oo2po
%attr(755,root,root) %{_bindir}/oo2xliff
%attr(755,root,root) %{_bindir}/php2po
%attr(755,root,root) %{_bindir}/phppo2pypo
%attr(755,root,root) %{_bindir}/po2csv
%attr(755,root,root) %{_bindir}/po2html
%attr(755,root,root) %{_bindir}/po2ical
%attr(755,root,root) %{_bindir}/po2idml
%attr(755,root,root) %{_bindir}/po2ini
%attr(755,root,root) %{_bindir}/po2json
%attr(755,root,root) %{_bindir}/po2moz
%attr(755,root,root) %{_bindir}/po2mozlang
%attr(755,root,root) %{_bindir}/po2oo
%attr(755,root,root) %{_bindir}/po2php
%attr(755,root,root) %{_bindir}/po2prop
%attr(755,root,root) %{_bindir}/po2rc
%attr(755,root,root) %{_bindir}/po2resx
%attr(755,root,root) %{_bindir}/po2sub
%attr(755,root,root) %{_bindir}/po2symb
%attr(755,root,root) %{_bindir}/po2tiki
%attr(755,root,root) %{_bindir}/po2tmx
%attr(755,root,root) %{_bindir}/po2ts
%attr(755,root,root) %{_bindir}/po2txt
%attr(755,root,root) %{_bindir}/po2web2py
%attr(755,root,root) %{_bindir}/po2wordfast
%attr(755,root,root) %{_bindir}/po2xliff
%attr(755,root,root) %{_bindir}/poclean
%attr(755,root,root) %{_bindir}/pocommentclean
%attr(755,root,root) %{_bindir}/pocompendium
%attr(755,root,root) %{_bindir}/pocompile
%attr(755,root,root) %{_bindir}/poconflicts
%attr(755,root,root) %{_bindir}/pocount
%attr(755,root,root) %{_bindir}/podebug
%attr(755,root,root) %{_bindir}/pofilter
%attr(755,root,root) %{_bindir}/pogrep
%attr(755,root,root) %{_bindir}/pomerge
%attr(755,root,root) %{_bindir}/pomigrate2
%attr(755,root,root) %{_bindir}/popuretext
%attr(755,root,root) %{_bindir}/poreencode
%attr(755,root,root) %{_bindir}/porestructure
%attr(755,root,root) %{_bindir}/posegment
%attr(755,root,root) %{_bindir}/posplit
%attr(755,root,root) %{_bindir}/poswap
%attr(755,root,root) %{_bindir}/pot2po
%attr(755,root,root) %{_bindir}/poterminology
%attr(755,root,root) %{_bindir}/pretranslate
%attr(755,root,root) %{_bindir}/prop2po
%attr(755,root,root) %{_bindir}/pydiff
%attr(755,root,root) %{_bindir}/pypo2phppo
%attr(755,root,root) %{_bindir}/rc2po
%attr(755,root,root) %{_bindir}/resx2po
%attr(755,root,root) %{_bindir}/sub2po
%attr(755,root,root) %{_bindir}/symb2po
%attr(755,root,root) %{_bindir}/tiki2po
%attr(755,root,root) %{_bindir}/tmserver
%attr(755,root,root) %{_bindir}/ts2po
%attr(755,root,root) %{_bindir}/txt2po
%attr(755,root,root) %{_bindir}/web2py2po
%attr(755,root,root) %{_bindir}/xliff2odf
%attr(755,root,root) %{_bindir}/xliff2oo
%attr(755,root,root) %{_bindir}/xliff2po
%if %{with doc}
%{_mandir}/man1/csv2po.1*
%{_mandir}/man1/csv2tbx.1*
%{_mandir}/man1/html2po.1*
%{_mandir}/man1/ical2po.1*
%{_mandir}/man1/ini2po.1*
%{_mandir}/man1/json2po.1*
%{_mandir}/man1/moz2po.1*
%{_mandir}/man1/odf2xliff.1*
%{_mandir}/man1/oo2po.1*
%{_mandir}/man1/oo2xliff.1*
%{_mandir}/man1/php2po.1*
%{_mandir}/man1/po2csv.1*
%{_mandir}/man1/po2html.1*
%{_mandir}/man1/po2ical.1*
%{_mandir}/man1/po2ini.1*
%{_mandir}/man1/po2json.1*
%{_mandir}/man1/po2moz.1*
%{_mandir}/man1/po2oo.1*
%{_mandir}/man1/po2php.1*
%{_mandir}/man1/po2prop.1*
%{_mandir}/man1/po2rc.1*
%{_mandir}/man1/po2resx.1*
%{_mandir}/man1/po2sub.1*
%{_mandir}/man1/po2symb.1*
%{_mandir}/man1/po2tiki.1*
%{_mandir}/man1/po2tmx.1*
%{_mandir}/man1/po2ts.1*
%{_mandir}/man1/po2txt.1*
%{_mandir}/man1/po2web2py.1*
%{_mandir}/man1/po2wordfast.1*
%{_mandir}/man1/po2xliff.1*
%{_mandir}/man1/poclean.1*
%{_mandir}/man1/pocompile.1*
%{_mandir}/man1/poconflicts.1*
%{_mandir}/man1/podebug.1*
%{_mandir}/man1/pofilter.1*
%{_mandir}/man1/pogrep.1*
%{_mandir}/man1/pomerge.1*
%{_mandir}/man1/porestructure.1*
%{_mandir}/man1/posegment.1*
%{_mandir}/man1/poswap.1*
%{_mandir}/man1/pot2po.1*
%{_mandir}/man1/poterminology.1*
%{_mandir}/man1/pretranslate.1*
%{_mandir}/man1/prop2po.1*
%{_mandir}/man1/rc2po.1*
%{_mandir}/man1/resx2po.1*
%{_mandir}/man1/sub2po.1*
%{_mandir}/man1/symb2po.1*
%{_mandir}/man1/tiki2po.1*
%{_mandir}/man1/ts2po.1*
%{_mandir}/man1/txt2po.1*
%{_mandir}/man1/web2py2po.1*
%{_mandir}/man1/xliff2odf.1*
%{_mandir}/man1/xliff2oo.1*
%{_mandir}/man1/xliff2po.1*
%endif

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/langmodels
%{_datadir}/%{name}/langmodels/README
%{_datadir}/%{name}/stoplist-en
%{_datadir}/%{name}/langmodels/fpdb.conf

%lang(af) %{_datadir}/%{name}/langmodels/afrikaans.lm
%lang(ar) %{_datadir}/%{name}/langmodels/arabic.lm
%lang(be) %{_datadir}/%{name}/langmodels/belarus.lm
%lang(br) %{_datadir}/%{name}/langmodels/breton.lm
%lang(bs) %{_datadir}/%{name}/langmodels/bosnian.lm
%lang(ca) %{_datadir}/%{name}/langmodels/catalan.lm
%lang(cy) %{_datadir}/%{name}/langmodels/welsh.lm
%lang(cz) %{_datadir}/%{name}/langmodels/czech.lm
%lang(da) %{_datadir}/%{name}/langmodels/danish.lm
%lang(de) %{_datadir}/%{name}/langmodels/german.lm
%lang(el) %{_datadir}/%{name}/langmodels/greek.lm
%lang(en) %{_datadir}/%{name}/langmodels/english.lm
%lang(eo) %{_datadir}/%{name}/langmodels/esperanto.lm
%lang(es) %{_datadir}/%{name}/langmodels/spanish.lm
%lang(et) %{_datadir}/%{name}/langmodels/estonian.lm
%lang(eu) %{_datadir}/%{name}/langmodels/basque.lm
%lang(fi) %{_datadir}/%{name}/langmodels/finnish.lm
%lang(fr) %{_datadir}/%{name}/langmodels/french.lm
%lang(fy) %{_datadir}/%{name}/langmodels/frisian.lm
%lang(ga) %{_datadir}/%{name}/langmodels/irish_gaelic.lm
%lang(gd) %{_datadir}/%{name}/langmodels/scots.lm
%lang(gd) %{_datadir}/%{name}/langmodels/scots_gaelic.lm
%lang(gv) %{_datadir}/%{name}/langmodels/manx_gaelic.lm
%lang(he) %{_datadir}/%{name}/langmodels/hebrew.lm
%lang(hr) %{_datadir}/%{name}/langmodels/croatian.lm
%lang(hu) %{_datadir}/%{name}/langmodels/hungarian.lm
%lang(id) %{_datadir}/%{name}/langmodels/indonesian.lm
%lang(is) %{_datadir}/%{name}/langmodels/icelandic.lm
%lang(it) %{_datadir}/%{name}/langmodels/italian.lm
%lang(ja) %{_datadir}/%{name}/langmodels/japanese.lm
%lang(lt) %{_datadir}/%{name}/langmodels/lithuanian.lm
%lang(lv) %{_datadir}/%{name}/langmodels/latvian.lm
%lang(ms) %{_datadir}/%{name}/langmodels/malay.lm
%lang(nd) %{_datadir}/%{name}/langmodels/Ndebele.lm
%lang(nl) %{_datadir}/%{name}/langmodels/dutch.lm
%lang(no) %{_datadir}/%{name}/langmodels/norwegian.lm
%lang(po) %{_datadir}/%{name}/langmodels/polish.lm
%lang(pt) %{_datadir}/%{name}/langmodels/portuguese.lm
%lang(qu) %{_datadir}/%{name}/langmodels/quechua.lm
%lang(rm) %{_datadir}/%{name}/langmodels/romansh.lm
%lang(ro) %{_datadir}/%{name}/langmodels/romanian.lm
%lang(ru) %{_datadir}/%{name}/langmodels/russian.lm
%lang(sk) %{_datadir}/%{name}/langmodels/slovenian.lm
%lang(sk@latin) %{_datadir}/%{name}/langmodels/slovak_ascii.lm
%lang(sq) %{_datadir}/%{name}/langmodels/albanian.lm
%lang(sr) %{_datadir}/%{name}/langmodels/latin.lm
%lang(sr@latin) %{_datadir}/%{name}/langmodels/serbian_ascii.lm
%lang(ss) %{_datadir}/%{name}/langmodels/Swati.lm
%lang(st) %{_datadir}/%{name}/langmodels/NorthernSotho.lm
%lang(st) %{_datadir}/%{name}/langmodels/Sotho.lm
%lang(sv) %{_datadir}/%{name}/langmodels/swedish.lm
%lang(sw) %{_datadir}/%{name}/langmodels/swahili.lm
%lang(tl) %{_datadir}/%{name}/langmodels/tagalog.lm
%lang(tn) %{_datadir}/%{name}/langmodels/Tswana.lm
%lang(tr) %{_datadir}/%{name}/langmodels/turkish.lm
%lang(ts) %{_datadir}/%{name}/langmodels/Tsonga.lm
%lang(uk) %{_datadir}/%{name}/langmodels/ukrainian.lm
%lang(ve) %{_datadir}/%{name}/langmodels/Venda.lm
%lang(vi) %{_datadir}/%{name}/langmodels/vietnamese.lm
%lang(xh) %{_datadir}/%{name}/langmodels/Xhosa.lm
%lang(zh_CN) %{_datadir}/%{name}/langmodels/chinese_simplified.lm
%lang(zh_TW) %{_datadir}/%{name}/langmodels/chinese_traditional.lm
%lang(zu) %{_datadir}/%{name}/langmodels/Zulu.lm

%dir %{py_sitescriptdir}/translate
%{py_sitescriptdir}/translate/*.py[co]
%{py_sitescriptdir}/translate/convert
%{py_sitescriptdir}/translate/filters
%{py_sitescriptdir}/translate/misc
%{py_sitescriptdir}/translate/search
%{py_sitescriptdir}/translate/services
%{py_sitescriptdir}/translate/storage
%{py_sitescriptdir}/translate/tools
%{py_sitescriptdir}/translate_toolkit-*.egg-info

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc translate/doc/api/*
%endif
