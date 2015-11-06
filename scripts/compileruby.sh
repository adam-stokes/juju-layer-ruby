#!/bin/bash

cat > /etc/gemrc <<EOF
install: --no-rdoc --no-ri
update: --no-rdoc --no-ri
EOF

{

    export RUBY_CFLAGS="-O3 -Wno-error=shorten-64-to-32 $RUBY_CFLAGS";
    ./configure --prefix=/usr --disable-install-rdoc;
    make -j`nproc`;
    make install;

} > /tmp/ruby/build.log
