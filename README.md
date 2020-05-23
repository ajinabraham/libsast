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

## Command Line Options

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


## Example Usage

```json
$ libsast -s tests/unit/assets/rules/semantic_grep/ -p tests/unit/assets/rules/pattern_matcher/ tests/unit/assets/files/
{
  "pattern_matcher": {
    "test_regex": {
      "files": [
        {
          "file_path": "tests/unit/assets/files/test_matcher.test",
          "match_position": [
            1143,
            1151
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
    }
  },
  "semantic_grep": {
    "errors": [],
    "matches": {
      "boto-client-ip": {
        "files": [
          {
            "file_path": "tests/unit/assets/files/test_file.py",
            "match_lines": [
              3,
              3
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
>>> options = {'match_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/pattern_matcher', 'sgrep_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/semantic_grep', 'sgrep_binary': None, 'sgrep_extensions': {'', '.js'}, 'match_extensions': {'.hbs', '.sh', '.ejs', '.toml', '.mustache', '.tmpl', '.jade', '.json', '.ect', '.vue', '.yml', '.hdbs', '.tl', '.html', '.haml', '.dust', '.pug', '.tpl'}, 'ignore_filenames': {'bootstrap.min.js', '.DS_Store', 'bootstrap-tour.js', 'd3.min.js', 'tinymce.js', 'codemirror.js', 'tinymce.min.js', 'react-dom.production.min.js', 'react.js', 'jquery.min.js', 'react.production.min.js', 'codemirror-compressed.js', 'axios.min.js', 'angular.min.js', 'raphael-min.js', 'vue.min.js'}, 'ignore_extensions': {'.7z', '.exe', '.rar', '.zip', '.a', '.o', '.tz'}, 'ignore_paths': {'__MACOSX', 'jquery', 'fixtures', 'node_modules', 'bower_components', 'example', 'spec'}, 'show_progress': False}
>>> paths = ['../njsscan/tests/assets/dot_njsscan/']
>>> scanner = Scanner(options, paths)
>>> scanner.scan()
{'pattern_matcher': {'handlebar_mustache_template': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/ignore_ext.hbs', 'match_string': '{{{html}}}', 'match_position': (52, 62)}], 'metadata': {'id': 'handlebar_mustache_template', 'description': 'The Handlebar.js/Mustache.js template has an unescaped variable. Untrusted user input passed to this variable results in Cross Site Scripting (XSS).', 'type': 'Regex', 'pattern': '{{{.+}}}|{{[ ]*&[\\w]+.*}}', 'severity': 'ERROR', 'input_case': 'exact', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'owasp': 'A1: Injection'}}}, 'semantic_grep': {'matches': {'node_aes_ecb': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/lorem_scan.js', 'match_position': (16, 86), 'match_lines': (14, 14), 'match_string': "let decipher = crypto.createDecipheriv('aes-128-ecb', Buffer.from(ENCRYPTION_KEY), iv);"}], 'metadata': {'owasp': 'A9: Using Components with Known Vulnerabilities', 'cwe': 'CWE-327: Use of a Broken or Risky Cryptographic Algorithm', 'description': 'AES with ECB mode is deterministic in nature and not suitable for encrypting large amount of repetitive data.', 'severity': 'ERROR'}}, 'node_deserialize': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (19, 44), 'match_lines': (8, 8), 'match_string': '        var obj = serialize.unserialize(str);'}], 'metadata': {'owasp': 'A8: Insecure Deserialization', 'cwe': 'CWE-502: Deserialization of Untrusted Data', 'description': "User controlled data in 'unserialize()' or 'deserialize()' function can result in Object Injection or Remote Code Injection.", 'severity': 'ERROR'}}, 'express_xss': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip.js', 'match_position': (9, 52), 'match_lines': (7, 10), 'match_string': '        var str = new Buffer(req.cookies.profile, \'base64\').toString();\n\n        var obj = serialize.unserialize(str);\n\n        if (obj.username) {\n\n            res.send("Hello " + escape(obj.username));'}], 'metadata': {'owasp': 'A1: Injection', 'cwe': "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')", 'description': 'Untrusted User Input in Response will result in Reflected Cross Site Scripting Vulnerability.', 'severity': 'ERROR'}}, 'node_tls_reject': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 58), 'match_lines': (9, 9), 'match_string': "        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';"}, {'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (9, 55), 'match_lines': (18, 18), 'match_string': '        process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-295: Improper Certificate Validation', 'description': "Setting 'NODE_TLS_REJECT_UNAUTHORIZED' to 0 will allow node server to accept self signed certificates and is not an secure behaviour.", 'severity': 'ERROR'}}, 'node_curl_ssl_verify_disable': {'files': [{'file_path': '../njsscan/tests/assets/dot_njsscan/skip_dir/skip_me.js', 'match_position': (5, 35), 'match_lines': (45, 50), 'match_string': '    curl(url,\n\n        {\n\n            SSL_VERIFYPEER: 0\n\n        },\n\n        function (err) {\n\n            response.end(this.body);'}], 'metadata': {'owasp': 'A6: Security Misconfiguration', 'cwe': 'CWE-599: Missing Validation of OpenSSL Certificate', 'description': 'SSL Certificate verification for node-curl is disabled.', 'severity': 'ERROR'}}}, 'errors': []}}
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
1. Regex - if re.findall(regex1, input)
2. RegexAnd - if re.findall(regex1, input) and re.findall(regex2, input)
3. RegexOr - if re.findall(regex1, input) or re.findall(regex2, input)
4. RegexAndOr -  if (string1 in input)
                and ((string2 in input) or (string3 in input))
5. RegexAndNot - if(string1 in input and string2 not in input)
```
Example: [Pattern Matcher Rule](https://github.com/ajinabraham/libsast/blob/master/tests/unit/assets/rules/pattern_matcher/patterns.yaml)

Test your pattern matcher rules

`$ libsast -p tests/unit/assets/rules/pattern_matcher/patterns.yaml tests/unit/assets/files/`

### Semantic Grep

Semantic Grep uses [semgrep](https://github.com/returntocorp/semgrep), a fast and syntax-aware semantic code pattern search for many languages: like grep but for code.

Currently it supports Python, Java, JavaScript, Go and C.

Use [semgrep.live](https://semgrep.live/vAb) to write semantic grep rule patterns.

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

See semgrep documentation [here](https://github.com/returntocorp/semgrep/blob/develop/docs/configuration-files.md).

Example: [Semantic Grep Rule](https://github.com/ajinabraham/libsast/blob/master/tests/unit/assets/rules/semantic_grep/sgrep.yaml)

Test your semgrep rules

`$ libsast -s tests/unit/assets/rules/semantic_grep/sgrep.yaml tests/unit/assets/files/`

## Realworld Implementations

* [njsscan](https://github.com/ajinabraham/njsscan) SAST is built with libsast pattern matcher and semantic grep.
