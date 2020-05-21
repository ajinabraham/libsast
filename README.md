Generic SAST for Security Engineers. Powered by regex based pattern matcher and semantic aware [semgrep](https://github.com/returntocorp/semgrep).

[![PyPI version](https://badge.fury.io/py/libsast.svg)](https://badge.fury.io/py/libsast)
[![platform](https://img.shields.io/badge/platform-osx%2Flinux-green.svg)](https://github.com/ajinabraham/libsast)
[![License](https://img.shields.io/:license-lgpl2.1-blue.svg)](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)
[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/)

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ajinabraham/libsast.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ajinabraham/libsast/context:python)
[![Requirements Status](https://requires.io/github/ajinabraham/libsast/requirements.svg?branch=master)](https://requires.io/github/ajinabraham/libsast/requirements/?branch=master)
[![Build](https://github.com/ajinabraham/libsast/workflows/Build/badge.svg)](https://github.com/ajinabraham/libsast/actions?query=workflow%3ABuild)

## Install

`pip install libsast`

Supports only Mac and Linux

## Command line options

```bash
$ libsast
usage: libsast [-h] [-o OUTPUT] [-p PATTERN_FILE] [-s SGREP_PATTERN_FILE]
               [-b SGREP_BINARY]
               [--sgrep-file-extensions SGREP_FILE_EXTENSIONS [SGREP_FILE_EXTENSIONS ...]]
               [--file-extensions FILE_EXTENSIONS [FILE_EXTENSIONS ...]]
               [--ignore-filenames IGNORE_FILENAMES [IGNORE_FILENAMES ...]]
               [--ignore-extensions IGNORE_EXTENSIONS [IGNORE_EXTENSIONS ...]]
               [--ignore-paths IGNORE_PATHS [IGNORE_PATHS ...]]
               [--show-progress] [-v]
               [path [path ...]]

positional arguments:
  path                  Path can be file(s) or directories

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename to save JSON report.
  -p PATTERN_FILE, --pattern-file PATTERN_FILE
                        YAML pattern file, directory or url
  -s SGREP_PATTERN_FILE, --sgrep-pattern-file SGREP_PATTERN_FILE
                        sgrep rules directory
  -b SGREP_BINARY, --sgrep-binary SGREP_BINARY
                        sgrep binary location
  --sgrep-file-extensions SGREP_FILE_EXTENSIONS [SGREP_FILE_EXTENSIONS ...]
                        File extensions that should be scanned with sgrep
  --file-extensions FILE_EXTENSIONS [FILE_EXTENSIONS ...]
                        File extensions that should be scanned with pattern
                        matcher
  --ignore-filenames IGNORE_FILENAMES [IGNORE_FILENAMES ...]
                        File name(s) to ignore
  --ignore-extensions IGNORE_EXTENSIONS [IGNORE_EXTENSIONS ...]
                        File extension(s) to ignore in lower case
  --ignore-paths IGNORE_PATHS [IGNORE_PATHS ...]
                        Path(s) to ignore
  --show-progress       Show scan progress
  -v, --version         Show libsast version
```


## Sample Usage

```bash
$ libsast -s ../njsscan/njsscan/rules/semantic_grep/ -p ../njsscan/njsscan/rules/pattern_matcher/ ../njsscan/tests/assets/dot_njsscan/
{
  "pattern_matcher": {
    "handlebar_mustache_template": {
      "files": [
        {
          "file_path": "../njsscan/tests/assets/dot_njsscan/ignore_ext.hbs",
          "match_position": [
            52,
            62
          ],
          "match_string": "{{{html}}}"
        }
      ],
      "metadata": {
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "description": "The Handlebar.js/Mustache.js template has an unescaped variable. Untrusted user input passed to this variable results in Cross Site Scripting (XSS).",
        "id": "handlebar_mustache_template",
        "input_case": "exact",
        "owasp": "A1: Injection",
        "pattern": "{{{.+}}}|{{[ ]*&[\\w]+.*}}",
        "severity": "ERROR",
        "type": "Regex"
      }
    },
    "pug_jade_template": {
      "files": [
        {
          "file_path": "../njsscan/tests/assets/dot_njsscan/no_ext_scan",
          "match_position": [
            18,
            24
          ],
          "match_string": "!{'}'}"
        }
      ],
      "metadata": {
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "description": "The Pug.js/Jade.js template has an unescaped variable. Untrusted user input passed to this variable results in Cross Site Scripting (XSS).",
        "id": "pug_jade_template",
        "input_case": "exact",
        "owasp": "A1: Injection",
        "pattern": "!{.+}",
        "severity": "ERROR",
        "type": "Regex"
      }
    },
    "underscore_template": {
      "files": [
        {
          "file_path": "../njsscan/tests/assets/dot_njsscan/scan.new",
          "match_position": [
            285,
            307
          ],
          "match_string": "_.unescape(escapedStr)"
        }
      ],
      "metadata": {
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "description": "The Underscore unescape function with untrusted user input results in Cross Site Scripting (XSS).",
        "id": "underscore_template",
        "input_case": "exact",
        "owasp": "A1: Injection",
        "pattern": "_.unescape\\(.+\\)",
        "severity": "ERROR",
        "type": "Regex"
      }
    }
  },
  "semantic_grep": {
    "errors": [],
    "matches": {
      "express_xss": {
        "files": [
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/skip.js",
            "match_lines": [
              7,
              10
            ],
            "match_position": [
              9,
              52
            ],
            "match_string": "        var str = new Buffer(req.cookies.profile, 'base64').toString();\n\n        var obj = serialize.unserialize(str);\n\n        if (obj.username) {\n\n            res.send(\"Hello \" + escape(obj.username));"
          }
        ],
        "metadata": {
          "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
          "description": "Untrusted User Input in Response will result in Reflected Cross Site Scripting Vulnerability.",
          "owasp": "A1: Injection",
          "severity": "ERROR"
        }
      },
      "node_aes_ecb": {
        "files": [
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/lorem_scan.js",
            "match_lines": [
              14,
              14
            ],
            "match_position": [
              16,
              86
            ],
            "match_string": "let decipher = crypto.createDecipheriv('aes-128-ecb', Buffer.from(ENCRYPTION_KEY), iv);"
          }
        ],
        "metadata": {
          "cwe": "CWE-327: Use of a Broken or Risky Cryptographic Algorithm",
          "description": "AES with ECB mode is deterministic in nature and not suitable for encrypting large amount of repetitive data.",
          "owasp": "A9: Using Components with Known Vulnerabilities",
          "severity": "ERROR"
        }
      },
      "node_curl_ssl_verify_disable": {
        "files": [
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js",
            "match_lines": [
              45,
              50
            ],
            "match_position": [
              5,
              35
            ],
            "match_string": "    curl(url,\n\n        {\n\n            SSL_VERIFYPEER: 0\n\n        },\n\n        function (err) {\n\n            response.end(this.body);"
          }
        ],
        "metadata": {
          "cwe": "CWE-599: Missing Validation of OpenSSL Certificate",
          "description": "SSL Certificate verification for node-curl is disabled.",
          "owasp": "A6: Security Misconfiguration",
          "severity": "ERROR"
        }
      },
      "node_deserialize": {
        "files": [
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/skip.js",
            "match_lines": [
              8,
              8
            ],
            "match_position": [
              19,
              44
            ],
            "match_string": "        var obj = serialize.unserialize(str);"
          }
        ],
        "metadata": {
          "cwe": "CWE-502: Deserialization of Untrusted Data",
          "description": "User controlled data in 'unserialize()' or 'deserialize()' function can result in Object Injection or Remote Code Injection.",
          "owasp": "A8: Insecure Deserialization",
          "severity": "ERROR"
        }
      },
      "node_tls_reject": {
        "files": [
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js",
            "match_lines": [
              9,
              9
            ],
            "match_position": [
              9,
              58
            ],
            "match_string": "        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';"
          },
          {
            "file_path": "../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js",
            "match_lines": [
              18,
              18
            ],
            "match_position": [
              9,
              55
            ],
            "match_string": "        process.env.NODE_TLS_REJECT_UNAUTHORIZED = \"0\";"
          }
        ],
        "metadata": {
          "cwe": "CWE-295: Improper Certificate Validation",
          "description": "Setting 'NODE_TLS_REJECT_UNAUTHORIZED' to 0 will allow node server to accept self signed certificates and is not an secure behaviour.",
          "owasp": "A6: Security Misconfiguration",
          "severity": "ERROR"
        }
      }
    }
  }
}
```

## Python API

```python
>>> from libsast import Scanner
>>> options = {'match_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/pattern_matcher', 'sgrep_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/semantic_grep', 'sgrep_binary': None, 'sgrep_extensions': {'', '.js'}, 'match_extensions': {'.hbs', '.sh', '.ejs', '.toml', '.mustache', '.tmpl', '.jade', '.json', '.ect', '.vue', '.yml', '.hdbs', '.tl', '.html', '.haml', '.dust', '.pug', '.tpl'}, 'ignore_filenames': {'bootstrap.min.js', '.DS_Store', 'bootstrap-tour.js', 'd3.min.js', 'tinymce.js', 'codemirror.js', 'tinymce.min.js', 'react-dom.production.min.js', 'react.js', 'jquery.min.js', 'react.production.min.js', 'codemirror-compressed.js', 'axios.min.js', 'angular.min.js', 'raphael-min.js', 'vue.min.js'}, 'ignore_extensions': {'.7z', '.exe', '.rar', '.zip', '.a', '.o', '.tz'}, 'ignore_paths': {'__MACOSX', 'jquery', 'fixtures', 'node_modules', 'bower_components', 'example', 'spec'}, 'show_progress': False}
>>> paths = ['../njsscan/tests/assets/dot_njsscan/']
>>> scanner = Scanner(options, paths)
>>> scanner.scan()
{'pattern_matcher': {'handlebar_mustache_template': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/ignore_ext.hbs', 'match_string': '{{{html}}}', 'match_position': (52, 62)}], 'metadata': {'id': 'handlebar_mustache_template', 'description': 'The Handlebar.js/Mustache.js template has an unescaped variable. Untrusted user input passed to this variable results in Cross Site Scripting (XSS).', 'type': 'Regex', 'pattern': '{{{.+}}}|{{[ ]*&[\\w]+.*}}', 'severity': 'ERROR', 'input_case': 'exact', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'owasp': 'A1: Injection'}}}, 'semantic_grep': {'matches': {'node_aes_ecb': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (16, 86), 'match_lines': (14, 14), 'match_string': "let decipher = crypto.createDecipheriv('aes-128-ecb', Buffer.from(ENCRYPTION_KEY), iv);"}], 'metadata': {'owasp': 'A9: Using Components with Known Vulnerabilities', 'cwe': 'CWE-327: Use of a Broken or Risky Cryptographic Algorithm', 'description': 'AES with ECB mode is deterministic in nature and not suitable for encrypting large amount of repetitive data.', 'severity': 'ERROR'}}, 'node_deserialize': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (19, 44), 'match_lines': (8, 8), 'match_string': '        var obj = serialize.unserialize(str);'}], 'metadata': {'owasp': 'A8: Insecure Deserialization', 'cwe': 'CWE-502: Deserialization of Untrusted Data', 'description': "User controlled data in 'unserialize()' or 'deserialize()' function can result in Object Injection or Remote Code Injection.", 'severity': 'ERROR'}}, 'express_xss': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (9, 52), 'match_lines': (7, 10), 'match_string': '        var str = new Buffer(req.cookies.profile, \'base64\').toString();\n\n        var obj = serialize.unserialize(str);\n\n        if (obj.username) {\n\n            res.send("Hello " + escape(obj.username));'}], 'metadata': {'owasp': 'A1: Injection', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'description': 'Untrusted User Input in Response will result in Reflected Cross Site Scripting Vulnerability.', 'severity': 'ERROR'}}, 'node_tls_reject': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 58), 'match_lines': (9, 9), 'match_string': "        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';"}, {'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 55), 'match_lines': (18, 18), 'match_string': '        process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-295: Improper Certificate Validation', 'description': "Setting 'NODE_TLS_REJECT_UNAUTHORIZED' to 0 will allow node server to accept self signed certificates and is not an secure behaviour.", 'severity': 'ERROR'}}, 'node_curl_ssl_verify_disable': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (5, 35), 'match_lines': (45, 50), 'match_string': '    curl(url,\n\n        {\n\n            SSL_VERIFYPEER: 0\n\n        },\n\n        function (err) {\n\n            response.end(this.body);'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-599: Missing Validation of OpenSSL Certificate', 'description': 'SSL Certificate verification for node-curl is disabled.', 'severity': 'ERROR'}}}, 'errors': []}}
```
