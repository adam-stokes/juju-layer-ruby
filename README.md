# layer-ruby
> Juju charms.reactive layer for Ruby

# emitters

**ruby.available** - This state is automatically emitted once Ruby has been
installed. Rely on this state to perform an application deployment when Ruby
is ready to be used.

# api

All helper modules are found in `lib/charms/layer/ruby.py` available `from charms.layer import ruby`

Example,

```python

from charms.layer.ruby import bundle, gem, ruby_dist_dir

print(ruby_dist_dir())
# /var/lib/juju/agents/unit-ruby-0/charm/dist

@when('ruby.available')
def install_deps():
    bundle('install')
    gem('install dotenv')
    bundle('exec rails s')

```

# configuration

You can add additional debian packages to your ruby install by editing a
`layer.yaml` and placing the package names as follows

```
options:
  basic:
    packages:
      - libxml2-dev
      - libyaml-dev
```

This layer will pick up those dependencies in addition to the required packages
for ruby compilation.

# license

The MIT License (MIT)

Copyright (c) 2015 Adam Stokes <adam.stokes@ubuntu.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
