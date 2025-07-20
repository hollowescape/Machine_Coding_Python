Understanding the Problem & Clarifying Questions
Before diving into the design, I'll clarify a few points and state my assumptions.

Clarifying Questions (and my assumed answers for this design):

File System Entry Names: What characters are allowed in file/directory names? Are there any reserved characters (e.g., /, . ..)?

Assumption: Names are standard alphanumeric strings. / is strictly a path separator. ., .. are not explicitly supported for navigation; all paths are absolute from root. Names will not contain /.

Case Sensitivity: Are file and directory names case-sensitive (e.g., file.txt and File.txt are different)?

Assumption: Case-sensitive. my_folder and My_Folder are distinct entries.

Maximum Path Length/Depth: Are there any limits to the depth of the directory structure or length of paths?

Assumption: No explicit limits for this in-memory implementation, but in real systems, these would exist.

Content Size: Is there a limit on the size of file content?

Assumption: No explicit limit; content is a simple string.

cp and mv Destination Intermediates: The problem states cp and mv do not auto-create intermediate directories for the destination. Just to be super clear, if I cp /a/b.txt /x/y/z/new_b.txt, must /x/y/z already exist?

Confirmed: Yes, the parent directory of the destination_path must exist for cp and mv. Only mkdir and touch auto-create intermediates.

rm on Non-Empty Directory: The problem states rm deletes an "empty directory." What if rm /a is called and /a contains files or subdirectories?

Confirmed: It should raise an error if the directory is not empty.

mv - Moving Directory into Self/Subdirectory: The problem states "Raises an error if moving a directory into itself or a subdirectory (e.g., mv /a /a/b).". What about mv /a /a?

Confirmed: Moving a directory to its exact same path (effectively a no-op) should also be considered an error, or at least a non-operation that doesn't change anything, but for an error-driven design, raising an InvalidPathError would be fine. I'll consider it an error.