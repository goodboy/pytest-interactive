Change Log
==========
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres to
`Semantic Versioning`_.

.. _Keep a Changelog: http://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/


0.1.4 - 2017-11-30
------------------
Fixed
*****
- Hot fix for hard coding of wrong root node name (issue `#21`_).

.. _#21: https://github.com/tgoodlet/pytest-interactive/issues/21


0.1.3 - 2017-11-26
------------------
Added
*****
- Add ``pytest`` cache integration support (PR `#16`_).

Changed
*******
- Look for ``pytest.Item`` not ``pytest.Function``. Thanks to `@vodik`_ for
  PR `#17`_.

Fixed
*****
- Use ``node.name`` attribute to key test items/nodes (PR `#20`_).

.. _#16: https://github.com/tgoodlet/pytest-interactive/pull/16
.. _#17: https://github.com/tgoodlet/pytest-interactive/pull/17
.. _#20: https://github.com/tgoodlet/pytest-interactive/pull/20
.. _@vodik: https://github.com/vodik


0.1.2 - 2017-11-26
------------------
Botched release - ignore.


0.1.1 - 2016-09-19
------------------
Changed
*******
- Move to IPython 5.0+ and use the new `prompts`_ API. No support has
  been kept for previous IPython versions but this does not affect
  the plugin's cli in any noticable way.

.. _prompts: http://ipython.readthedocs.io/en/stable/config/details.html#custom-prompts


0.1 - 2016-08-02
----------------
Added
*****
- Initial plugin release which supports up to IPython 5.0 and includes
  docs but no unit tests.
