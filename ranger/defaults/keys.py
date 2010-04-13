# Copyright (C) 2009, 2010  Roman Zimbelmann <romanz@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This is the default key configuration file of ranger.
Syntax for binding keys: map(*keys, fnc)

Examples for keys: "x", "gg", "<C-J><A-4>", "<tab>", "<down><up><right>"

fnc is a function which is called with the CommandArgs object.

The CommandArgs object has these attributes:
arg.fm: the file manager instance
arg.wdg: the widget or ui instance
arg.n: the number typed before the key combination (if allowed)
arg.direction: the direction object (if applicable)
arg.keys: the string representation of the used key combination
arg.keybuffer: the keybuffer instance

Direction keys are special.  They must be mapped with: map.dir(*keys, **args)
where args is a dict of values such as up, down, to, absolute, relative...
Example: map.dir('gg', to=0)
Direction keys can be accessed in a mapping that contians "<dir>".

Additionally, there are shortcuts for accessing methods of the current
file manager and widget instance:
map('xyz', fm.method(foo=bar))
will be translated to:
map('xyz', lamdba arg: arg.fm.method(foo=bar))
If possible, arg.n and arg.direction are automatically inserted.


Example scenario
----------------
If this keys are defined:
map("dd", "d<dir>", fm.cut(foo=bar))
map.dir("gg", to=0)

Type in the keys on the left and the function on the right will be executed:
dd        => fm.cut(foo=bar)
5dd       => fm.cut(foo=bar, narg=5)
dgg       => fm.cut(foo=bar, dirarg=Direction(to=0))
5dgg      => fm.cut(foo=bar, narg=5, dirarg=Direction(to=0))
5d3gg     => fm.cut(foo=bar, narg=5, dirarg=Direction(to=3))
"""

from ranger.api.keys import *
from ranger import log

# ===================================================================
# == Define keys for everywhere:
# ===================================================================
map = global_keys = KeyMapWithDirections()
map('Q', fm.exit())
map('<C-L>', fm.redraw_window())
map('<backspace2>', alias='<backspace>')  # Backspace is bugged sometimes

#map('<dir>', wdg.move())
@map('<dir>') # move around with direction keys
def move(arg):
	arg.wdg.move(narg=arg.n, **arg.direction)

# -------------------------------------------------- direction keys
map.dir('<down>', down=1)
map.dir('<up>', down=-1)
map.dir('<left>', right=-1)
map.dir('<right>', right=1)
map.dir('<home>', down=0, absolute=True)
map.dir('<end>', down=-1, absolute=True)
map.dir('<pagedown>', down=1, pages=True)
map.dir('<pageup>', down=-1, pages=True)
map.dir('%', down=1, percentage=True, absolute=True)


# ===================================================================
# == Define aliases
# ===================================================================
map = vim_aliases = KeyMapWithDirections()
map.dir('j', alias='<down>')
map.dir('k', alias='<up>')
map.dir('h', alias='<left>')
map.dir('l', alias='<right>')
map.dir('gg', alias='<home>')
map.dir('G', alias='<end>')
map.dir('<C-F>', alias='<pagedown>')
map.dir('<C-B>', alias='<pageup>')

map = readline_aliases = KeyMapWithDirections()
map.dir('<C-B>', alias='<left>')
map.dir('<C-F>', alias='<right>')
map.dir('<C-A>', alias='<home>')
map.dir('<C-E>', alias='<end>')
map.dir('<C-D>', alias='<delete>')
map.dir('<C-H>', alias='<backspace>')


# ===================================================================
# == Define keys in "general" context:
# ===================================================================
map = keymanager['general']
map.merge(global_keys)
map.merge(vim_aliases)

# -------------------------------------------------------- movement
map('gg', fm.move(to=0))
map('<C-D>', 'J', fm.move(down=0.5, pages=True))
map('<C-U>', 'K', fm.move(up=0.5, pages=True))

# --------------------------------------------------------- history
map('H', fm.history_go(-1))
map('L', fm.history_go(1))

# ----------------------------------------------- tagging / marking
map('t', fm.tag_toggle())
map('T', fm.tag_remove())

map(' ', fm.mark(toggle=True))
map('v', fm.mark(all=True, toggle=True))
map('V', fm.mark(all=True, val=False))

# ------------------------------------------ file system operations
map('yy', 'y<dir>', fm.copy())
map('dd', 'd<dir>', fm.cut())
map('ud', fm.uncut())
map('pp', fm.paste())
map('po', fm.paste(overwrite=True))
map('pl', fm.paste_symlink())
map('p<bg>', fm.hint('press //p// once again to confirm pasting' \
		', or //l// to create symlinks'))

# ---------------------------------------------------- run programs
map('s', fm.execute_command(os.environ['SHELL']))
map('E', fm.edit_file())
map('.term', fm.execute_command('x-terminal-emulator', flags='d'))
map('du', fm.execute_command('du --max-depth=1 -h | less'))

# -------------------------------------------------- toggle options
map('z<bg>', fm.hint("show_//h//idden //p//review_files" \
	"//d//irectories_first //c//ollapse_preview flush//i//nput"))
map('zh', fm.toggle_boolean_option('show_hidden'))
map('zp', fm.toggle_boolean_option('preview_files'))
map('zi', fm.toggle_boolean_option('flushinput'))
map('zd', fm.toggle_boolean_option('directories_first'))
map('zc', fm.toggle_boolean_option('collapse_preview'))

# ------------------------------------------------------------ sort
map('o<bg>', 'O<bg>', fm.hint("//s//ize //b//ase//n//ame //m//time" \
	" //t//ype //r//everse"))
sort_dict = {
	's': 'size',
	'b': 'basename',
	'n': 'basename',
	'm': 'mtime',
	't': 'type',
}

for key, val in sort_dict.items():
	for key, is_capital in ((key, False), (key.upper(), True)):
		# reverse if any of the two letters is capital
		map('o' + key, fm.sort(func=val, reverse=is_capital))
		map('O' + key, fm.sort(func=val, reverse=True))

map('or', 'Or', 'oR', 'OR', lambda arg: \
		arg.fm.sort(reverse=not arg.fm.settings.sort_reverse))

# ----------------------------------------------- console shortcuts
@map("A")
def append_to_filename(arg):
	command = 'rename ' + arg.fm.env.cf.basename
	arg.fm.open_console(cmode.COMMAND, command)

map('cw', fm.open_console(cmode.COMMAND, 'rename '))
map('cd', fm.open_console(cmode.COMMAND, 'cd '))
map('f', fm.open_console(cmode.COMMAND_QUICK, 'find '))
map('bf', fm.open_console(cmode.COMMAND, 'filter '))
map('d<bg>', fm.hint('d//u// (disk usage) d//d// (cut)'))
map('@', fm.open_console(cmode.OPEN, '@'))
map('#', fm.open_console(cmode.OPEN, 'p!'))

# --------------------------------------------- jump to directories
map('gh', fm.cd('~'))
map('ge', fm.cd('/etc'))
map('gu', fm.cd('/usr'))
map('gd', fm.cd('/dev'))
map('gl', fm.cd('/lib'))
map('go', fm.cd('/opt'))
map('gv', fm.cd('/var'))
map('gr', 'g/', fm.cd('/'))
map('gm', fm.cd('/media'))
map('gn', fm.cd('/mnt'))
map('gs', fm.cd('/srv'))
map('gR', fm.cd(RANGERDIR))

# ------------------------------------------------------------ tabs
map('gc', '<C-W>', fm.tab_close())
map('gt', '<TAB>', fm.tab_move(1))
map('gT', '<S-TAB>', fm.tab_move(-1))
map('gn', '<C-N>', fm.tab_new())
for n in range(1, 10):
	map('g' + str(n), fm.tab_open(n))
	map('<A-' + str(n) + '>', fm.tab_open(n))

# ------------------------------------------------------- searching
map('/', fm.open_console(cmode.SEARCH))

map('n', fm.search())
map('N', fm.search(forward=False))

map('ct', fm.search(order='tag'))
map('cc', fm.search(order='ctime'))
map('cm', fm.search(order='mimetype'))
map('cs', fm.search(order='size'))
map('c<bg>', fm.hint('//c//time //m//imetype //s//ize'))

# ------------------------------------------------------- bookmarks
for key in ALLOWED_BOOKMARK_KEYS:
	map("`" + key, "'" + key, fm.enter_bookmark(key))
	map("m" + key, fm.set_bookmark(key))
	map("um" + key, fm.unset_bookmark(key))
map("`<bg>", "'<bg>", "m<bg>", fm.draw_bookmarks())

# ---------------------------------------------------- change views
map('i', fm.display_file())
map('<C-P>', fm.display_log())
map('?', KEY_F1, fm.display_help())
map('w', lambda arg: arg.fm.ui.open_taskview())

# ------------------------------------------------ system functions
map('ZZ', 'ZQ', fm.exit())
map('<C-R>', fm.reset())
map('R', fm.reload_cwd())
@map('<C-C>')
def ctrl_c(arg):
	try:
		item = arg.fm.loader.queue[0]
	except:
		arg.fm.notify("Type Q or :quit<Enter> to exit Ranger")
	else:
		arg.fm.notify("Aborting: " + item.get_description())
		arg.fm.loader.remove(index=0)

map(':', ';', fm.open_console(cmode.COMMAND))
map('>', fm.open_console(cmode.COMMAND_QUICK))
map('!', fm.open_console(cmode.OPEN))
map('r', fm.open_console(cmode.OPEN_QUICK))


# ===================================================================
# == Define keys for the pager
# ===================================================================
map = pager_keys = KeyMapWithDirections()
map.merge(global_keys)
map.merge(vim_aliases)

# -------------------------------------------------------- movement
map('<left>', wdg.move(left=4))
map('<right>', wdg.move(right=4))
map('<C-D>', 'd', wdg.move(down=0.5, pages=True))
map('<C-U>', 'u', wdg.move(up=0.5, pages=True))
map('<C-F>', 'f', '<pagedown>', wdg.move(down=1, pages=True))
map('<C-B>', 'b', '<pageup>', wdg.move(up=1, pages=True))
map('<space>', wdg.move(down=0.8, pages=True))
map('<cr>', wdg.move(down=1))

# ---------------------------------------------------------- others
map('E', fm.edit_file())
map('?', fm.display_help())

# --------------------------------------------------- bind the keys
# There are two different kinds of pagers, each have a different
# method for exiting:

map = keymanager.get_context('pager')
map.merge(pager_keys)
map('q', 'i', '<esc>', lambda arg: arg.fm.ui.close_pager())

map = keymanager.get_context('embedded_pager')
map.merge(pager_keys)
map('q', 'i', '<esc>', lambda arg: arg.fm.ui.close_embedded_pager())


# ===================================================================
# == Define keys for the taskview
# ===================================================================
map = keymanager.get_context('taskview')
map('K', wdg.task_move(0))
map('J', wdg.task_move(-1))
map('dd', wdg.task_remove())

map('?', fm.display_help())
map('w', 'q', ESC, ctrl('d'), ctrl('c'),
		lambda arg: arg.fm.ui.close_taskview())


# ===================================================================
# == Define keys for the console
# ===================================================================
map = keymanager.get_context('console')
map.merge(global_keys)
map.merge(readline_aliases)

map('<up>', wdg.history_move(-1))
map('<down>', wdg.history_move(1))
map('<home>', wdg.move(right=0, absolute=True))
map('<end>', wdg.move(right=-1, absolute=True))
map('<tab>', wdg.tab())
map('<s-tab>', wdg.tab(-1))
map('<c-c>', '<esc>', wdg.close())
map('<CR>', '<c-j>', wdg.execute())
map('<F1>', lambda arg: arg.fm.display_command_help(arg.wdg))

map('<backspace>', wdg.delete(-1))
map('<delete>', wdg.delete(1))
map('<C-W>', wdg.delete_word())
map('<C-K>', wdg.delete_rest(1))
map('<C-U>', wdg.delete_rest(-1))
map('<C-Y>', wdg.paste())

# Any key which is still undefined will simply be typed in.
@map('<any>')
def type_key(arg):
	arg.wdg.type_key(arg.match)

# Unmap some global keys so we can type them:
map.unmap('Q')
map.directions.unmap('%')
