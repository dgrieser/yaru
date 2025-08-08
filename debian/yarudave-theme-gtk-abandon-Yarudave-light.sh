#!/bin/sh

yarudave_light_name="'Yarudave-light'"
yarudave_new_name="'Yarudave'"

if [ "$(gsettings get org.gnome.desktop.interface gtk-theme)" = "$yarudave_light_name" ]; then
    gsettings set org.gnome.desktop.interface gtk-theme "$yarudave_new_name"
fi

if [ "$(gsettings get org.gnome.gedit.preferences.editor scheme)" = "$yarudave_light_name" ]; then
    gsettings set org.gnome.gedit.preferences.editor scheme "$yarudave_new_name"
fi
