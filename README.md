# extracao-noticias-ciencia

Scripts de extração de títulos de notícias, datas e tags/palavras-chave de revistas universitárias e portais de ciências. Desenvolvido em 2015, talvez sejam necessárias adaptações para o correto funcionamento das extrações.

## Fontes para extração:

* Agência USP de Notícias
* USP Online
* Canal Ciência IBICT
* Ciência e Cultura
* Ciência Hoje
* Divulga Ciência UFSC
* Fapesp
* Jornal da Ciência
* Minas Faz Ciência
* ~~UnB Ciência~~
* ~~Unesp Ciência~~
* ~~Unicamp JU~~


```
sudo pip2 install -r requirements.txt

python2 agenusp_usponline.py extrai_agenusp
python2 agenusp_usponline.py extrai_usponline
python2 jornal_da_ciencia.py extrai_jornal_da_ciencia
python2 fapesp.py extrai_fapesp
```
