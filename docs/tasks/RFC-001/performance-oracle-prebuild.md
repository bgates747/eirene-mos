The first device-free oracle self-test stopped at header parsing: MOS=B08C80B8
was incorrectly treated as decimal metadata. No compiler or target ran. Parser
now excludes nonnumeric identity fields; numeric measurement/state validation
is unchanged. Original error was retained in this session; rerun is a new host
validation of the corrected parser, not a relabelled target result.
