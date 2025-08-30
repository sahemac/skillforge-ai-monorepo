| Type MIME / Extension(s) | Librairie OSS / Méthode | Sortie (str) | Notes Techniques |
| --- | --- | --- | --- |
| application/pdf | pdfminer.six | Texte brut | Doit gérer les documents multi-colonnes et tenter d'extraire le texte dans un ordre de lecture logique. |
| .docx | python-docx | Texte brut | Extraction du contenu des paragraphes et des tableaux. |
| .pptx | python-pptx | Texte des diapositives | Concaténation du texte de toutes les zones de texte et des notes du présentateur. |
| .xlsx | pandas | Texte formaté (CSV) | Concaténation du contenu textuel de toutes les cellules de toutes les feuilles en une chaîne de caractères unique. |
| .md, .txt | builtin | Texte brut | Lecture directe du fichier. |
| .json, .yml, .yaml | builtin + json/pyyaml | Texte formaté | Conversion du contenu structuré en une chaîne de caractères indentée pour préserver la structure. |
| .html, .css | BeautifulSoup4 | Texte / Code | Pour HTML, extraction du contenu textuel visible (en ignorant les balises <script> et <style>). Pour CSS, utilisation du code brut. |
| .js, .jsx, .ts, .tsx | builtin | Code source | Lecture directe du code source. |
| .py, .ipynb | builtin + nbformat | Code source | Pour les notebooks, extraction du contenu des cellules de code et de Markdown. |

