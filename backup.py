#!/usr/bin/python2
# -*- coding: utf8 -*-

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
import sys
import ConfigParser

# libs locais
import utils

# Classe que representa um alvo de backup
class BackupTarget():
    def __init__(self, source, destiny, protocol_type, compress_type = "xz"):
        # TODO: implementar validação da entrada. Todos os atributos iniciais
        # devem ser strings.
        self.source_path = source     # caminho do arquivo original
        self.destiny = destiny        # url do destino do backup (será utilizado o mesmo path da fonte)
        self.protocol = protocol_type # protocolo para realização do backup (ssh, rsync etc.)
        self.compress = compress_type # tipo de compactação possivelmente utilizada

    def run_backup(self):
        # TODO: implementar verificações para outros protocolos
        """ Realiza as operações de backup """
        if self.protocol == "rsync":
            status = utils.rsync(self.source_path, self.destiny)
        return status

    def pack(self):
        """
         Compacta o arquivo/diretório do alvo de backup. O novo alvo passa a
         ser um arquivo compactado em /tmp
        """
        new_path = utils.compress(self.compress, self.source_path)
        if new_path != "":
            self.source_path = new_path
        else:
            print >> sys.stdout, "Erro na compactação do arquivo, utilizando arquivo original"

# TODO: testar funcionamento do gerador de lista de pacotes
def listaDePacotes(pkglist_file = "~/.pkg_list"):
    """ Função que gera a lista dos pacotes instalados no sistema """
    os.system("dpkg -l '*' > " + pkglist_file)
    return pkglist_file

# iniciando a execução do script

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
# TODO: permitir a utilização de variáveis de bash em caminhos de arquivo
# é obrigatória, com todos os seus membros, e os tipos devem ser verificados
CONFIG_FILES = ["/etc/caco_backup.conf","/home/ivan/.caco_backup.conf"]
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILES)

backup_list = []
for bfile in config.get("defaults", "files").split(","):
    backup_list.append(BackupTarget(bfile, config.get("defaults", "destination"),
                                    config.get("defaults", "protocol")))

for backup in backup_list:
    backup.run_backup()
