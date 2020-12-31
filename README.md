# libsast

Generic SAST for Security Engineers. Powered by regex based pattern matcher and semantic aware [semgrep](https://github.com/returntocorp/semgrep).

Made with ![Love](https://cloud.githubusercontent.com/assets/4301109/16754758/82e3a63c-4813-11e6-9430-6015d98aeaab.png) in India [![Tweet](https://img.shields.io/twitter/url?url=https://github.com/ajinabraham/libsast)](https://twitter.com/intent/tweet/?text=Generic%20SAST%20for%20Security%20Engineers.%20Powered%20by%20regex%20based%20pattern%20matcher%20and%20semantic%20aware%20semgrep%20by%20%40ajinabraham%20%40OpenSecurity_IN&url=https://github.com/ajinabraham/libsast)

[![PyPI version](https://badge.fury.io/py/libsast.svg)](https://badge.fury.io/py/libsast)
[![platform](https://img.shields.io/badge/platform-windows%2Fosx%2Flinux-green.svg)](https://github.com/ajinabraham/libsast)
[![License](https://img.shields.io/:license-lgpl2.1-blue.svg)](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)
[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/)

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ajinabraham/libsast.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ajinabraham/libsast/context:python)
[![Requirements Status](https://requires.io/github/ajinabraham/libsast/requirements.svg?branch=master)](https://requires.io/github/ajinabraham/libsast/requirements/?branch=master)
[![Build](https://github.com/ajinabraham/libsast/workflows/Build/badge.svg)](https://github.com/ajinabraham/libsast/actions?query=workflow%3ABuild)

### Support libsast

* **Donate via Paypal:** [![Donate via Paypal](https://user-images.githubusercontent.com/4301109/76471686-c43b0500-63c9-11ea-8225-2a305efb3d87.gif)](https://paypal.me/ajinabraham)
* **Sponsor the Project:** [![Github Sponsors](https://user-images.githubusercontent.com/4301109/95517226-9e410780-098e-11eb-9ef5-7b8c7561d725.png)](https://github.com/sponsors/ajinabraham)

## Install

`pip install libsast`

Pattern Matcher is cross-platform, but Semgrep supports only Mac and Linux.

## Command Line Options

```bash
$ libsast
usage: libsast [-h] [-o OUTPUT] [-p PATTERN_FILE] [-s SGREP_PATTERN_FILE]
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


## Example Usage

```json
$ libsast -s tests/assets/rules/semantic_grep/ -p tests/assets/rules/pattern_matcher/ tests/assets/files/
{
  "pattern_matcher": {
    "test_regex": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            28,
            28
          ],
          "match_position": [
            1141,
            1149
          ],
          "match_string": ".close()"
        }
      ],
      "metadata": {
        "description": "This is a rule to test regex",
        "id": "test_regex",
        "input_case": "exact",
        "pattern": "\\.close\\(\\)",
        "severity": "info",
        "type": "Regex"
      }
    },
    "test_regex_and": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            3,
            3
          ],
          "match_position": [
            52,
            66
          ],
          "match_string": "webkit.WebView"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            7,
            7
          ],
          "match_position": [
            194,
            254
          ],
          "match_string": ".loadUrl(\"file:/\" + Environment.getExternalStorageDirectory("
        }
      ],
      "metadata": {
        "description": "This is a rule to test regex_and",
        "id": "test_regex_and",
        "input_case": "exact",
        "pattern": [
          "\\.loadUrl\\(.*getExternalStorageDirectory\\(",
          "webkit\\.WebView"
        ],
        "severity": "error",
        "type": "RegexAnd"
      }
    },
    "test_regex_and_not": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            42,
            42
          ],
          "match_position": [
            1415,
            1424
          ],
          "match_string": "WKWebView"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            40,
            40
          ],
          "match_position": [
            1363,
            1372
          ],
          "match_string": "WKWebView"
        }
      ],
      "metadata": {
        "description": "This is a rule to test regex_and_not",
        "id": "test_regex_and_not",
        "input_case": "exact",
        "pattern": [
          "WKWebView",
          "\\.javaScriptEnabled=false"
        ],
        "severity": "warning",
        "type": "RegexAndNot"
      }
    },
    "test_regex_and_or": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            50,
            50
          ],
          "match_position": [
            1551,
            1571
          ],
          "match_string": "telephony.SmsManager"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            58,
            58
          ],
          "match_position": [
            1973,
            1988
          ],
          "match_string": "sendTextMessage"
        }
      ],
      "metadata": {
        "description": "This is a rule to test regex_and_or",
        "id": "test_regex_and_or",
        "input_case": "exact",
        "pattern": [
          "telephony.SmsManager",
          [
            "sendMultipartTextMessage",
            "sendTextMessage",
            "vnd.android-dir/mms-sms"
          ]
        ],
        "severity": "warning",
        "type": "RegexAndOr"
      }
    },
    "test_regex_multiline": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            52,
            52
          ],
          "match_position": [
            1586,
            1684
          ],
          "match_string": "public void onRequestPermissionsResult(int requestCode,String permissions[], int[] grantResults) {"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            10,
            11
          ],
          "match_position": [
            297,
            368
          ],
          "match_string": "public static ForgeAccount add(Context context, ForgeAccount account) {"
        }
      ],
      "metadata": {
        "cwe": "cwe-1002",
        "description": "This is a rule to test regex",
        "id": "test_regex_multiline",
        "input_case": "exact",
        "masvs": "MSTG-STORAGE-3",
        "owasp-mobile": "M1: Improper Platform Usage",
        "owasp-web": "A10: Insufficient Logging & Monitoring",
        "pattern": "((?:public.+)+)",
        "severity": "info",
        "type": "Regex"
      }
    },
    "test_regex_or": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            26,
            26
          ],
          "match_position": [
            1040,
            1067
          ],
          "match_string": "Context.MODE_WORLD_READABLE"
        }
      ],
      "metadata": {
        "description": "This is a rule to test regex_or",
        "id": "test_regex_or",
        "input_case": "exact",
        "pattern": [
          "MODE_WORLD_READABLE|Context\\.MODE_WORLD_READABLE",
          "openFileOutput\\(\\s*\".+\"\\s*,\\s*1\\s*\\)"
        ],
        "severity": "error",
        "type": "RegexOr"
      }
    }
  },
  "semantic_grep": {
    "errors": [
      {
        "code": 3,
        "help": "If the code appears to be valid, this may be a semgrep bug.",
        "level": "warn",
        "long_msg": "Could not parse test_matcher.test as python",
        "short_msg": "parse error",
        "spans": [
          {
            "context_end": null,
            "context_start": null,
            "end": {
              "col": 24,
              "line": 40
            },
            "file": "test_matcher.test",
            "source_hash": "84d2247435a86d69a88bc7d9d63cd03454490865c6271d5a4815a3d717f8d8d9",
            "start": {
              "col": 23,
              "line": 40
            }
          }
        ],
        "type": "SourceParseError"
      },
      {
        "code": 3,
        "help": "If the code appears to be valid, this may be a semgrep bug.",
        "level": "warn",
        "long_msg": "Could not parse test_matcher.test as javascript",
        "short_msg": "parse error",
        "spans": [
          {
            "context_end": null,
            "context_start": null,
            "end": {
              "col": 1,
              "line": 1
            },
            "file": "test_matcher.test",
            "source_hash": "84d2247435a86d69a88bc7d9d63cd03454490865c6271d5a4815a3d717f8d8d9",
            "start": {
              "col": 1,
              "line": 1
            }
          }
        ],
        "type": "SourceParseError"
      }
    ],
    "matches": {
      "boto-client-ip": {
        "files": [
          {
            "file_path": "tests/assets/files/example_file.py",
            "match_lines": [
              4,
              4
            ],
            "match_position": [
              24,
              31
            ],
            "match_string": "8.8.8.8"
          }
        ],
        "metadata": {
          "cwe": "CWE Category",
          "description": "boto client using IP address",
          "owasp": "OWASP Category",
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
>>> options = {'match_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/pattern_matcher', 'sgrep_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/semantic_grep', 'sgrep_extensions': {'', '.js'}, 'match_extensions': {'.hbs', '.sh', '.ejs', '.toml', '.mustache', '.tmpl', '.jade', '.json', '.ect', '.vue', '.yml', '.hdbs', '.tl', '.html', '.haml', '.dust', '.pug', '.tpl'}, 'ignore_filenames': {'bootstrap.min.js', '.DS_Store', 'bootstrap-tour.js', 'd3.min.js', 'tinymce.js', 'codemirror.js', 'tinymce.min.js', 'react-dom.production.min.js', 'react.js', 'jquery.min.js', 'react.production.min.js', 'codemirror-compressed.js', 'axios.min.js', 'angular.min.js', 'raphael-min.js', 'vue.min.js'}, 'ignore_extensions': {'.7z', '.exe', '.rar', '.zip', '.a', '.o', '.tz'}, 'ignore_paths': {'__MACOSX', 'jquery', 'fixtures', 'node_modules', 'bower_components', 'example', 'spec'}, 'show_progress': False}
>>> paths = ['../njsscan/tests/assets/dot_njsscan/']
>>> scanner = Scanner(options, paths)
>>> scanner.scan()
{'pattern_matcher': {'handlebar_mustache_template': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/ignore_ext.hbs', 'match_string': '{{{html}}}', 'match_position': (52, 62), 'match_lines': (1, 1)}], 'metadata': {'id': 'handlebar_mustache_template', 'description': 'The Handlebar.js/Mustache.js template has an unescaped variable. Untrusted user input passed to this variable results in Cross Site Scripting (XSS).', 'type': 'Regex', 'pattern': '{{{.+}}}|{{[ ]*&[\\w]+.*}}', 'severity': 'ERROR', 'input_case': 'exact', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'owasp': 'A1: Injection'}}}, 'semantic_grep': {'matches': {'node_aes_ecb': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (16, 87), 'match_lines': (14, 14), 'match_string': "let decipher = crypto.createDecipheriv('aes-128-ecb', Buffer.from(ENCRYPTION_KEY), iv);"}], 'metadata': {'owasp': 'A9: Using Components with Known Vulnerabilities', 'cwe': 'CWE-327: Use of a Broken or Risky Cryptographic Algorithm', 'description': 'AES with ECB mode is deterministic in nature and not suitable for encrypting large amount of repetitive data.', 'severity': 'ERROR'}}, 'node_tls_reject': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 58), 'match_lines': (9, 9), 'match_string': "        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';"}, {'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 55), 'match_lines': (18, 18), 'match_string': '        process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-295: Improper Certificate Validation', 'description': "Setting 'NODE_TLS_REJECT_UNAUTHORIZED' to 0 will allow node server to accept self signed certificates and is not a secure behaviour.", 'severity': 'ERROR'}}, 'node_curl_ssl_verify_disable': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (5, 11), 'match_lines': (45, 51), 'match_string': '    curl(url,\n\n        {\n\n            SSL_VERIFYPEER: 0\n\n        },\n\n        function (err) {\n\n            response.end(this.body);\n\n        })'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-599: Missing Validation of OpenSSL Certificate', 'description': 'SSL Certificate verification for node-curl is disabled.', 'severity': 'ERROR'}}, 'regex_injection_dos': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (5, 37), 'match_lines': (25, 27), 'match_string': '    var key = req.param("key");\n\n    // Regex created from user input\n\n    var re = new RegExp("\\\\b" + key);'}], 'metadata': {'owasp': 'A1: Injection', 'cwe': 'CWE-400: Uncontrolled Resource Consumption', 'description': 'User controlled data in RegExp() can make the application vulnerable to layer 7 DoS.', 'severity': 'ERROR'}}, 'express_xss': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (9, 55), 'match_lines': (7, 10), 'match_string': '        var str = new Buffer(req.cookies.profile, \'base64\').toString();\n\n        var obj = serialize.unserialize(str);\n\n        if (obj.username) {\n\n            res.send("Hello " + escape(obj.username));'}], 'metadata': {'owasp': 'A1: Injection', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'description': 'Untrusted User Input in Response will result in Reflected Cross Site Scripting Vulnerability.', 'severity': 'ERROR'}}, 'generic_path_traversal': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (5, 35), 'match_lines': (36, 37), 'match_string': "    var filePath = path.join(__dirname, '/' + req.query.load);\n\n    fileSystem.readFile(filePath); // ignore: generic_path_traversal"}, {'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (5, 35), 'match_lines': (42, 43), 'match_string': "    var filePath = path.join(__dirname, '/' + req.query.load);\n\n    fileSystem.readFile(filePath); // detect this"}], 'metadata': {'owasp': 'A5: Broken Access Control', 'cwe': 'CWE-23: Relative Path Traversal', 'description': 'Untrusted user input in readFile()/readFileSync() can endup in Directory Traversal Attacks.', 'severity': 'ERROR'}}, 'express_open_redirect': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (5, 26), 'match_lines': (49, 51), 'match_string': '    var target = req.param("target");\n\n    // BAD: sanitization doesn\'t apply here\n\n    res.redirect(target); //ignore: express_open_redirect'}], 'metadata': {'owasp': 'A1: Injection', 'cwe': "CWE-601: URL Redirection to Untrusted Site ('Open Redirect')", 'description': 'Untrusted user input in redirect() can result in Open Redirect vulnerability.', 'severity': 'ERROR'}}, 'node_deserialize': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (19, 45), 'match_lines': (8, 8), 'match_string': '        var obj = serialize.unserialize(str);'}], 'metadata': {'owasp': 'A8: Insecure Deserialization', 'cwe': 'CWE-502: Deserialization of Untrusted Data', 'description': "User controlled data in 'unserialize()' or 'deserialize()' function can result in Object Injection or Remote Code Injection.", 'severity': 'ERROR'}}}, 'errors': [{'type': 'SourceParseError', 'code': 3, 'short_msg': 'parse error', 'long_msg': 'Could not parse .njsscan as javascript', 'level': 'warn', 'spans': [{'start': {'line': 2, 'col': 20}, 'end': {'line': 2, 'col': 21}, 'source_hash': 'c60298be568bfb1325d92cbb3c0bc1450a25b85bb2e4000bdc3267c05f1c8c73', 'file': '.njsscan', 'context_start': None, 'context_end': None}], 'help': 'If the code appears to be valid, this may be a semgrep bug.'}, {'type': 'SourceParseError', 'code': 3, 'short_msg': 'parse error', 'long_msg': 'Could not parse no_ext_scan as javascript', 'level': 'warn', 'spans': [{'start': {'line': 1, 'col': 3}, 'end': {'line': 1, 'col': 5}, 'source_hash': 'f002e2a715be216987dd1b134e7b9fa6eef28e3caa82dead0109c4cdc489e089', 'file': 'no_ext_scan', 'context_start': None, 'context_end': None}], 'help': 'If the code appears to be valid, this may be a semgrep bug.'}]}}
```

## Write you own Static Analysis tool

With libsast, you can write your own static analysis tools. libsast provides two matching engines:

1. **Pattern Matcher**
2. **Semantic Grep**

### Pattern Matcher

Currently Pattern Matcher supports any language.

Use [Regex 101](https://regex101.com/r/nGbAay/1) to write simple Python Regex rule patterns.

A sample rule looks like

```yaml
- id: test_regex_or
  description: This is a rule to test regex_or
  input_case: exact
  pattern:
  - MODE_WORLD_READABLE|Context\.MODE_WORLD_READABLE
  - openFileOutput\(\s*".+"\s*,\s*1\s*\)
  severity: error
  type: RegexOr
  owasp: 'OWASP Category'
```
A rule consist of 

* `id` : A unique id for the rule
* `description`: A description for the rule
* `input_case`: It can be `exact`, `upper` or `lower`. Data will be converted to lower case/upper case/as it is before comparing with the regex.
* `pattern`: List of patterns depends on `type`.
* `severity`: It can be `error`, `warning` or `info`
* `type`: Pattern Matcher supports `Regex`, `RegexAnd`, `RegexOr`, `RegexAndOr`, `RegexAndNot`
* `custom_field`: Define your own custom fields that you can use as metadata

```bash
1. Regex - if regex1 in input
2. RegexAnd - if regex1 in input and regex2 in input
3. RegexOr - if regex1 in input or regex2 in input
4. RegexAndOr -  if regex1 in input and (regex2 in input or regex3 in input)
5. RegexAndNot - if regex1 in input and not regex2 in input
```
Example: [Pattern Matcher Rule](https://github.com/ajinabraham/libsast/blob/master/tests/assets/rules/pattern_matcher/patterns.yaml)

Test your pattern matcher rules

`$ libsast -p tests/assets/rules/pattern_matcher/patterns.yaml tests/assets/files/`

#### Inbuilt Standard Mapping Support

* [OWASP Web Top 10](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_web_top10_2017.yaml)
* [OWASP Mobile Top 10](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_mobile_top10_2016.yaml)
* [OWASP MASVS](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_masvs.yaml)
* [CWE](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/cwe.yaml)

### Semantic Grep

Semantic Grep uses [semgrep](https://github.com/returntocorp/semgrep), a fast and syntax-aware semantic code pattern search for many languages: like grep but for code.

Currently it supports Python, Java, JavaScript, Go and C.

Use [semgrep.dev](https://semgrep.dev/vAb) to write semantic grep rule patterns.

A sample rule for Python code looks like

```yaml
rules:
  - id: boto-client-ip
    patterns:
      - pattern-inside: boto3.client(host="...")
      - pattern-regex: '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    message: "boto client using IP address"
    languages: [python]
    severity: ERROR
    metadata:
      owasp: 'OWASP Category'
      cwe: 'CWE Category'
```

See semgrep documentation [here](https://semgrep.dev/docs/writing-rules/rule-syntax/).

Example: [Semantic Grep Rule](https://github.com/ajinabraham/libsast/blob/master/tests/assets/rules/semantic_grep/sgrep.yaml)

Test your semgrep rules

`$ libsast -s tests/assets/rules/semantic_grep/sgrep.yaml tests/assets/files/`

## Realworld Implementations

* [njsscan](https://github.com/ajinabraham/njsscan) SAST is built with libsast pattern matcher and semantic grep.
* [nodejsscan](https://github.com/ajinabraham/nodejsscan) nodejsscan is a static security code scanner for Node.js applications.
* [MobSF](https://mobsf.github.io/Mobile-Security-Framework-MobSF/) Static Code Analyzer for Android and iOS mobile applications.
