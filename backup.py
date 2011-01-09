#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Script para realizar backup das máquinas do CACo

# Copyrigth 2010,2011 Ivan Sichmann Freitas 
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

################################################################################
# Imports
################################################################################

import os
import ConfigParser
import logging
import optparse
import sys

################################################################################
# Classes
################################################################################

class Tools():
    # IMPORTANTE: para funcionar, precisa ter chave ssh e host do destino no
    # know_hosts do usuário
    def rsync(self, source, destinyURL, opts=""):
        """ Executa um rsync. O argumento 'opts' é opcional """
        # rsync -avLz
        rsync_command="rsync --archive --verbose --copy-links --compress"
        # executa o comando e guarda o status de retorno
        exit_status = os.system(" ".join([rsync_command, opts, source, destinyURL]))
        if exit_status != os.EX_OK:
            logger.error("Erro durante o rsync: " + format(exit_status))
        else:
            logger.info("Rsync de " + source + " para " + destinyURL+ " executado com sucesso")
        return exit_status
    def compress(self, compression_type, source, opts=""):
        """ Compacta um arquivo/diretório em algum lugar em /tmp, retonando o
        caminho desse novo arquivo """
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

# Classe que representa um alvo de backup
class BackupTarget(Tools):
    def __init__(self, source, destiny, protocol_type, compress_type = "xz"):
        self.source_path = source     # caminho do arquivo original
        self.destiny = destiny        # url do destino do backup (será utilizado o mesmo path da fonte)
        self.protocol = protocol_type # protocolo para realização do backup (ssh, rsync etc.)
        self.compress = compress_type # tipo de compactação possivelmente utilizada

    def run_backup(self):
        """ Realiza as operações de backup """
        if self.protocol == "rsync":
            status = self.rsync(self.source_path, self.destiny)
        else:
            logger.warning("Protocolo especificado é inexistente")
            status = os.EX_DATAERR
        return status

    def pack(self):
        """
        Compacta o arquivo/diretório do alvo de backup. O novo alvo passa a
        ser um arquivo compactado em /tmp
        """
        new_path = self.compress(self.compress, self.source_path)
        if new_path != "":
            self.source_path = new_path
        else:
            logger.error("Erro na compactação do arquivo, utilizando arquivo original")

################################################################################
# Funções
################################################################################

# TODO: testar funcionamento do gerador de lista de pacotes
def lista_de_pacotes(pkglist_file = "~/.pkg_list"):
    """ Função que gera a lista dos pacotes instalados no sistema """
    os.system("dpkg -l '*' > " + pkglist_file)
    return pkglist_file

################################################################################
# Iniciando a execução do script
################################################################################

if __name__ == "__main__":
    ################################################################################
    # Configurando o logging
    ################################################################################
    log_file = os.path.expandvars("${HOME}/caco_backup.log")
    if os.path.lexists(log_file):
        os.remove(log_file) # limpando o log antigo
    logging.basicConfig(filename=log_file,
                        format="%(asctime)s: %(name)s:%(levelname)s %(message)s")
    logger = logging.getLogger("backup.py")
    logger.setLevel(logging.DEBUG)

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
    config_files = ["/etc/caco_backup.conf", os.path.expandvars("${HOME}/.caco_backup.conf")]
    config = ConfigParser.ConfigParser()
    config.read(config_files)

    # avaliando parâmetros de linha de comando
    options = optparse.OptionParser()
    # lista de opções, edite aqui se quiser adicionar/remover alguma opção
    options_list = [
        # [ opção curta, opção longa, help, valor padrão]
        ['-p', '--pretend', u'Apenas lista o que vai ser feito', False],
        ['-d', '--destino', u'Novo destino padrão, afeta apenas os arquivos \
         listados na seção "defaults" do arquivo de configuração', ''],
        ['-c', '--comprime', u'Força a compressão dos arquivos padrão com o \
         algoritmo especificado', ''],
        ['-t', '--protocol', u'Força o uso do protocolo especificado', '']
    ]
    # adicionando as opções
    for o in options_list:
        if type(o[3]) is str:
            options.add_option(o[0], o[1], help=o[2], default=o[3],
                               action="store")
        elif type(o[3]) is bool:
            options.add_option(o[0], o[1], help=o[2], default=o[3],
                               action="store_true")
    (opts, args) = options.parse_args(sys.argv)
    opt = {}
    # transformando as opções em string e depois em dicionário
    for o in format(opts).strip('{} ').split(','):
        lvalue = o.split(':')[0].strip("' '")
        rvalue = o.split(':')[1].strip("' '")
        if rvalue is '':
            opt[lvalue] = rvalue
        else:
            opt[lvalue] = eval(rvalue)

    backup_list = []
    for bfile in config.get("defaults", "files").split(","):
        backup_list.append(BackupTarget(bfile, config.get("defaults", "destination"),
                                        config.get("defaults", "protocol")))
        logger.info("Preparando backup de %s" %bfile)
    # com pretend apenas imprime origem e destino de cada arquivo do backup
    if opt['pretend'] is True:
        for bfile in backup_list:
            print bfile.source_path + " -> " +bfile.destiny
        sys.exit(os.EX_OK)
    map (lambda x: x.run_backup(), backup_list)
