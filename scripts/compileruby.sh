#!/bin/bash
{

    export RUBY_CFLAGS="-O3 -Wno-error=shorten-64-to-32 $RUBY_CFLAGS";
    ./configure --prefix=/usr;
    make;
    make install;

} > /tmp/ruby/build.log
