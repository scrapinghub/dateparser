# -*- coding: utf-8 -*-
import re

GROUPS_REGEX = re.compile(r'(?<=\\)(\d+|g<\d+>)')
G_REGEX = re.compile(r'g<(\d+)>')


def wrap_replacement_for_regex(replacement, regex):
    # prepend group to replacement
    replacement = r"\1%s" % increase_regex_replacements_group_positions(replacement, increment=1)

    # append group to replacement
    used_groups = re.compile(regex).groups
    new_group = used_groups + 2  # Consider that we already prepended replacement with one group
    replacement = "%s\\%d" % (replacement, new_group)

    return replacement


def increase_regex_replacements_group_positions(replacement, increment):
    splitted = GROUPS_REGEX.split(replacement)
    for i in range(1, len(splitted), 2):
        group = splitted[i]
        if group.isdigit():
            splitted[i] = str(int(group) + increment)
        else:
            splitted[i] = "g<{}>".format(int(G_REGEX.match(group).group(1)) + increment)
    return u"".join(splitted)
