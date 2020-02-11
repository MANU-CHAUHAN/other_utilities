def get_data_gen(file, file_type=None):
    for line in open(file, 'r'):
        line = line.strip()
        if line.endswith(","):
            line = line[:-1]
        if file_type and file_type.lower() == "raw":
            if not (line.startswith("[") or line.endswith("]")):
                yield line
        else:
            yield line


def convert_seconds_to_hms_format(seconds):
    mins = seconds // 60
    hours = str(mins // 60)
    mins = str(mins % 60)
    seconds = str(seconds % 60)
    return '0' * (2 - len(hours)) + hours + ' hours ' + '0' * (2 - len(mins)) + mins + ' minutes ' + '0' * (
            2 - len(seconds)) + seconds + ' seconds '