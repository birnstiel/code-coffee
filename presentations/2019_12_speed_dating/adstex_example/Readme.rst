Example Paper
=============

.. note::

	I used `adstex <https://github.com/yymao/adstex>`_ to generate
    ``bibliography.bib`` like this

    .. code-block::

        adstex aanda.tex --no-update

    This downloads new citations and puts them into ``bibliography.bib``. To
    have a more reasonable name for them, they can be renamed in the bibfile to
    an AuthorYEAR like label (like ``Ivlev2016`` instead of
    ``2016ApJ...833...92I``). This label can be used in the tex file and will be
    recognized by ``adstex``.

    The option ``--no-update`` speeds up the process. It can be left out to
    update the entries, in case something went from submitted to published, for
    example.
