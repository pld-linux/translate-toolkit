# TODO
# - fc gettext-libs is contained in "gettext-devel, libasprintf", but which exactly?
#
# Conditional build:
%bcond_without	apidocs		# do not package API docs
%bcond_without	doc			# do not package user docs

Summary:	Tools to assist with translation and software localization
Name:		translate-toolkit
Version:	1.8.0
Release:	1
License:	GPL v2+
Group:		Development/Tools
Source0:	http://downloads.sourceforge.net/project/translate/Translate%20Toolkit/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	6acc870d677d6312625e3e002d483b58
Patch0:		%{name}-stoplist.patch
Patch1:		%{name}-langmodel_dir.patch
Patch2:		unbash.patch
URL:		http://translate.sourceforge.net/wiki/toolkit/index
BuildRequires:	checkbashisms
BuildRequires:	python-dateutil
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	sed >= 4.0
# The following are needed for man page generation
BuildRequires:	python-lxml
BuildRequires:	python-simplejson
BuildRequires:	python-vobject
Requires:	python-iniparse
Requires:	python-lxml >= 2.1.0
Requires:	python-simplejson
Requires:	python-vobject
%ifarch %{ix86}
Requires:	python-psyco
%endif
Suggests:	iso-codes
Suggests:	python-Levenshtein
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

%build
checkbashisms tools/*
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install \
	--optimize=2 \
	--skip-build \
	--root $RPM_BUILD_ROOT

# create manpages
install -d $RPM_BUILD_ROOT%{_mandir}/man1
for program in $RPM_BUILD_ROOT%{_bindir}/*; do
	case $(basename $program) in
	  pocompendium|poen|pomigrate2|popuretext|poreencode|posplit|pocount|poglossary|lookupclient.py|tmserver|build_tmdb)
	   ;;
	  *)
		LC_ALL=C PYTHONPATH=. $program --manpage \
		  > $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1 \
		  || rm -f $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1
		  ;;
	esac
done

%py_postclean

# remove documentation files from site-packages
rm -r $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/doc
rm $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/{COPYING,ChangeLog,LICENSE,README}
rm $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/{convert,filters,tools}/TODO
rm $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/misc/README

# Move data files to %{_datadir}
mkdir  $RPM_BUILD_ROOT%{_datadir}/translate-toolkit
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/share/stoplist* $RPM_BUILD_ROOT%{_datadir}/translate-toolkit
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/share/langmodels $RPM_BUILD_ROOT%{_datadir}/translate-toolkit
rmdir $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/share

# we don't package tests
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/tools/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/convert/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/filters/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/lang/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/misc/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/search/indexing/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/search/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/placeables/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/test_*.py*
rm -f $RPM_BUILD_ROOT%{py_sitescriptdir}/translate/storage/xml_extract/test_*.py*

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
%doc translate/ChangeLog translate/README
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
%dir %{_datadir}/translate-toolkit

%dir %{_datadir}/%{name}/langmodels
%{_datadir}/%{name}/langmodels/README
%{_datadir}/%{name}/stoplist-en
%{_datadir}/%{name}/langmodels/fpdb.conf

%lang(af) %{_datadir}/%{name}/langmodels/afrikaans.lm
%lang(sq) %{_datadir}/%{name}/langmodels/albanian.lm
%lang(ar) %{_datadir}/%{name}/langmodels/arabic.lm
%lang(eu) %{_datadir}/%{name}/langmodels/basque.lm
%lang(be) %{_datadir}/%{name}/langmodels/belarus.lm
%lang(bs) %{_datadir}/%{name}/langmodels/bosnian.lm
%lang(br) %{_datadir}/%{name}/langmodels/breton.lm
%lang(ca) %{_datadir}/%{name}/langmodels/catalan.lm
%lang(zh_CN) %{_datadir}/%{name}/langmodels/chinese_simplified.lm
%lang(zh_TW) %{_datadir}/%{name}/langmodels/chinese_traditional.lm
%lang(hr) %{_datadir}/%{name}/langmodels/croatian.lm
%lang(cz) %{_datadir}/%{name}/langmodels/czech.lm
%lang(da) %{_datadir}/%{name}/langmodels/danish.lm
%lang(nl) %{_datadir}/%{name}/langmodels/dutch.lm
%lang(en) %{_datadir}/%{name}/langmodels/english.lm
%lang(eo) %{_datadir}/%{name}/langmodels/esperanto.lm
%lang(et) %{_datadir}/%{name}/langmodels/estonian.lm
%lang(fi) %{_datadir}/%{name}/langmodels/finnish.lm
%lang(fr) %{_datadir}/%{name}/langmodels/french.lm
%lang(fy) %{_datadir}/%{name}/langmodels/frisian.lm
%lang(de) %{_datadir}/%{name}/langmodels/german.lm
%lang(el) %{_datadir}/%{name}/langmodels/greek.lm
%lang(he) %{_datadir}/%{name}/langmodels/hebrew.lm
%lang(hu) %{_datadir}/%{name}/langmodels/hungarian.lm
%lang(is) %{_datadir}/%{name}/langmodels/icelandic.lm
%lang(id) %{_datadir}/%{name}/langmodels/indonesian.lm
%lang(ga) %{_datadir}/%{name}/langmodels/irish_gaelic.lm
%lang(it) %{_datadir}/%{name}/langmodels/italian.lm
%lang(ja) %{_datadir}/%{name}/langmodels/japanese.lm
%lang(sr) %{_datadir}/%{name}/langmodels/latin.lm
%lang(lv) %{_datadir}/%{name}/langmodels/latvian.lm
%lang(lt) %{_datadir}/%{name}/langmodels/lithuanian.lm
%lang(ms) %{_datadir}/%{name}/langmodels/malay.lm
%lang(gv) %{_datadir}/%{name}/langmodels/manx_gaelic.lm
%lang(no) %{_datadir}/%{name}/langmodels/norwegian.lm
%lang(po) %{_datadir}/%{name}/langmodels/polish.lm
%lang(pt) %{_datadir}/%{name}/langmodels/portuguese.lm
%lang(qu) %{_datadir}/%{name}/langmodels/quechua.lm
%lang(ro) %{_datadir}/%{name}/langmodels/romanian.lm
%lang(rm) %{_datadir}/%{name}/langmodels/romansh.lm
%lang(ru) %{_datadir}/%{name}/langmodels/russian.lm
%lang(gd) %{_datadir}/%{name}/langmodels/scots.lm
%lang(gd) %{_datadir}/%{name}/langmodels/scots_gaelic.lm
%lang(sr@latin) %{_datadir}/%{name}/langmodels/serbian_ascii.lm
%lang(sk@latin) %{_datadir}/%{name}/langmodels/slovak_ascii.lm
%lang(sk) %{_datadir}/%{name}/langmodels/slovenian.lm
%lang(es) %{_datadir}/%{name}/langmodels/spanish.lm
%lang(sw) %{_datadir}/%{name}/langmodels/swahili.lm
%lang(sv) %{_datadir}/%{name}/langmodels/swedish.lm
%lang(tl) %{_datadir}/%{name}/langmodels/tagalog.lm
%lang(tr) %{_datadir}/%{name}/langmodels/turkish.lm
%lang(uk) %{_datadir}/%{name}/langmodels/ukrainian.lm
%lang(vi) %{_datadir}/%{name}/langmodels/vietnamese.lm
%lang(cy) %{_datadir}/%{name}/langmodels/welsh.lm

%dir %{py_sitescriptdir}/translate
%{py_sitescriptdir}/translate/*.py[co]
%{py_sitescriptdir}/translate/convert
%{py_sitescriptdir}/translate/filters
%{py_sitescriptdir}/translate/misc
%{py_sitescriptdir}/translate/search
%{py_sitescriptdir}/translate/services
%{py_sitescriptdir}/translate/storage
%{py_sitescriptdir}/translate/tools
%if "%{py_ver}" > "2.4"
%{py_sitescriptdir}/translate_toolkit-*.egg-info
%endif

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc translate/doc/user/*
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc translate/doc/api/*
%endif
