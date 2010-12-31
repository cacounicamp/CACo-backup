#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Script para realizar backup das máquinas do CACo

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

# standard libs
import os
import ConfigParser
import logging

# libs locais
import utils

# configurando o logging
# TODO: configurar melhor a saída do log
LOG_FILE = "${HOME}/caco_backup.log"
logging.basicConfig(filename=os.path.expandvars(LOG_FILE))
logger = logging.getLogger("backup.py")
logger.setLevel(logging.DEBUG)

# Classe que representa um alvo de backup
class BackupTarget():
    def __init__(self, source, destiny, protocol_type, compress_type = "xz"):
        # FIXME: encontrar uma forma mais elegante para validação dos parâmetros, e aplicar onde for necessário
        if (type(source) != type(str()) or
            type(destiny) != type(str()) or
            type(protocol_type) != type(str()) or
            type(compress_type) != type(str())):
            logger.error("Argumentos inválidos para inicialização da classe BackupTarget")
        # devem ser strings.
        self.source_path = source     # caminho do arquivo original
        self.destiny = destiny        # url do destino do backup (será utilizado o mesmo path da fonte)
        self.protocol = protocol_type # protocolo para realização do backup (ssh, rsync etc.)
        self.compress = compress_type # tipo de compactação possivelmente utilizada

    def run_backup(self):
        """ Realiza as operações de backup """
        if self.protocol == "rsync":
            status = utils.rsync(self.source_path, self.destiny)
        else:
            logger.warning("Protocolo especificado é inexistente")
            status = os.EX_DATAERR
        return status

    # TODO: testar a função pack
    def pack(self):
        """
         Compacta o arquivo/diretório do alvo de backup. O novo alvo passa a
         ser um arquivo compactado em /tmp
        """
        new_path = utils.compress(self.compress, self.source_path)
        if new_path != "":
            self.source_path = new_path
        else:
            logger.error("Erro na compactação do arquivo, utilizando arquivo original")

### iniciando a execução do script

# lendo a configuração
# Exemplo de configuração:
# [defaults]
# destination = /home/ivan/teste
# protocol = rsync
# files = ~/.vimrc,~/.bashrc,~/.tmux.conf
# compression_type = xz
# use_compression = false
#
# [path_to_specific_files]
# # aqui vem as opções especiais, irão sobrescrever as padrão

# TODO: implementar a verificação por compressão
# TODO: implementar a verificação de seções especiais (i.e., arquivos com opções diferentes)
# TODO: implementar a validação do arquivo de configuração, somente a seção [defaults] 
# é obrigatória, com todos os seus membros, e os tipos devem ser verificados
logger.info("Iniciando o backup")
# TODO: logar a leitura da configuração
config_files = ["/etc/caco_backup.conf", os.path.expandvars("${HOME}/.caco_backup.conf")]
config = ConfigParser.ConfigParser()
config.read(config_files)

backup_list = []
for bfile in config.get("defaults", "files").split(","):
    backup_list.append(BackupTarget(bfile, config.get("defaults", "destination"),
                                    config.get("defaults", "protocol")))
    logger.info("Preparando backup de %s" %bfile)

map (lambda x: x.run_backup(), backup_list)
