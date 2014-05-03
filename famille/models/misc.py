# -*- coding=utf-8 -*-
from django.db import models

from famille.utils import DOCUMENT_TYPES
from famille.utils.fields import upload_to_timestamp, ContentTypeRestrictedFileField


__all__ = ["DownloadableFile", ]


class DownloadableFile(models.Model):

    KINDS = {
        "tools": u"Outils",
        "pratique": u"Fiches pratiques",
        "metiers": u"Fiches métiers",
    }

    name = models.CharField(max_length=50, verbose_name="Nom du fichier")
    description = models.CharField(max_length=150)
    file_content = ContentTypeRestrictedFileField(
        upload_to=upload_to_timestamp("downloadable_files"),
        content_types=DOCUMENT_TYPES.values(), extensions=DOCUMENT_TYPES.keys(),
        verbose_name="Fichier", max_upload_size=2621440  # 2.5MB
    )
    file_type = models.CharField(max_length=10, choices=KINDS.items(), verbose_name="Type de fichier")

    class Meta:
        app_label = 'famille'
        verbose_name = u'Fichier téléchargeable'
        verbose_name_plural = u'Fichiers téléchargeables'
