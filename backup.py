#!/usr/bin/python2

# -*- encoding: utf-8 -*-

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

import os
import sys
import utils

class BackupTarget():
	def __init__(self, source, destiny, protocol_type, compress_type = "xz"):
		# TODO: implementar validação da entrada. Todos os atributos iniciais
		# devem ser strings.
		self.source_path = source     # caminho do arquivo original
		self.destiny = destiny        # url do destino do backup (será utilizado o mesmo path da fonte)
		self.protocol = protocol_type # protocolo para realização do backup (ssh, rsync etc.)
		self.compress = compress_type # tipo de compactação possivelmente utilizada

	def run_backup(self):
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

# Roda o dpkg para pegar a lista de pacotes e retorna o caminho do arquivo criado
def listaDePacotes():
	""" Função que gera a lista dos pacotes instalados no sistema """
	pacotes = "~/.pkg_list"
	os.system("dpkg -l '*' >" + pacotes)
	return pacotes

# iniciando a execução do script

# TODO: implementar leitura de parâmetros a partir de um arquivo padrão em /etc
# TODO: implementar a execução normal do script =)
