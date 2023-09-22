from core.core10_parsing.cli.registry import command_registry

print(command_registry)

x = command_registry['mgr']['parser'].parse_known_args()
print(x)

#command_registry['mgr']['parser'].parse_known_args(['--help'])

x = command_registry['mgr']['parser'].parse_known_args(['-c', '/etc/x.yml', '--set', 'a=b', '--set', 'c=d', 'config', 'show', '--set', "u=v"])
print(x)
