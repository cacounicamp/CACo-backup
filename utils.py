# -*- coding: utf-8 -*-

# Funções para lidar com o rsync

# Copyrigth 2010 Ivan Sichmann Freitas 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

# TODO: mudar esse caminho
logging.basicConfig(filename="/home/ivan/caco_backup.log")

logger = logging.getLogger("utils.py")
logger.setLevel(logging.INFO)

# IMPORTANTE: para funcionar, precisa ter chave ssh e host do destino no
# know_hosts do usuário
def rsync(source, destinyURL, opts=""):
    """ Executa um rsync. O argumento 'opts' é opcional """
    if (type(source) != type(str()) or
        type(destinyURL) != type(str()) or
        type(opts) != type(str())):
        logger.error("Argumentos de 'rsync' não são strings")
        return os.EX_DATAERR
    # rsync -avLz
    rsync_command="rsync --archive --verbose --copy-links --compress"
    # executa o comando e guarda o status de retorno
    exit_status = os.system(" ".join([rsync_command, opts, source, destinyURL]))
    if exit_status != os.EX_OK:
        logger.error("Erro durante o rsync: " + format(exit_status))
    else:
        logger.info("Rsync de " + source + " para " + destinyURL+ " executado com sucesso")
    return exit_status

def compress(compression_type, source, opts=""):
    """ Compacta um arquivo/diretório em algum lugar em /tmp, retonando o
    caminho desse novo arquivo """
    if (type(compression_type) != type(str()) or
        type(source) != type(str()) or
        type(opts) != type(str())):
        logger.error("Argumentos de 'compress' não são strings")
        return os.EX_DATAERR

    # dicionário com os tipos de compressão e seus respectivos comandos
    compression_opts = {
        "xz":"tar -cJf",
        "gz":"tar -czf",
        "bz2": "tar -cjf"
    }
    tmp_file = os.tmpnam() + ".tar." + compression_type
    exit_status = os.system(" ".join([compression_opts[compression_type], opts, tmp_file, source]))
    if exit_status != os.EX_OK:
        logger.warning("Erro durante a compressão do arquivo: " + format(exit_status))
        tmp_file = "" # retornará string vazia para o caminho em caso de falha
    else:
        logger.info("Compressão de " + source + " realizada com sucesso")
    return tmp_file

# TODO: testar funcionamento do gerador de lista de pacotes
def listaDePacotes(pkglist_file = "~/.pkg_list"):
    """ Função que gera a lista dos pacotes instalados no sistema """
    if type(pkglist_file) != type(str()):
        logger.error("Argumento de 'listaDePacotes' não é string")
        return ""
    os.system("dpkg -l '*' > " + pkglist_file)
    return pkglist_file
