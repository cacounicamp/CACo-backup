# Funções para lidar com o rsync

# -*- encoding: utf-8 -*-

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

def rsync(source, destinyURL, opts=""):
	# TODO: verificar se os argumentos estão corretos
	""" Executa um rsync. O argumento 'opts' é opcional """
	# rsync -avLz
	rsync_command="rsync --archive --verbose --copy-links --compress"
	# executa o comando e guarda o status de retorno
	exit_status = os.system(rsync_command + opts + source + destinyURL)
	if exit_status != os.EX_OK:
		print >> sys.stdout, "Erro durante o rsync: %d" %exit_status
	return exit_status

def compress(compression_type, source, opts=""):
	""" Compacta um arquivo/diretório em algum lugar em /tmp, retonando o
	caminho desse novo arquivo """
	# TODO: validar argumentos
	compression_opts = {
		("xz","tar -cJf"),
		("gz","tar -czf"),
		("bz2", "tar -cjf")
	}
	tmp_file = tmpnam()
	exit_status = os.system(compression_opts[compression_type] + opts + tmp_file + source)
	if exit_status != os.EX_OK:
		print >> sys.stdout, "Erro durante a compressão do arquivo: %d" %exit_status
		tmp_file = "" # retornará string vazia para o caminho em caso de falha
	return tmp_file
