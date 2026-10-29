import subprocess as sp

sp.run("clear")
# sp.run("echo 'Hello World'", shell=True)
# sp.run("pwd")

# Convert docx to pdf
sp.run(["lowriter", "--convert-to", "pdf", "sample.docx", "--outdir", "./results/doc2pdf"])

# convert multiple docx to pdf
# sp.run(["lowriter", "--convert-to", "pdf", "*.docx"])

# Convert ppts to pdf
sp.run(["lowriter", "--convert-to", "pdf", "sample.pptx", "--outdir", "./results/ppt2pdf"])

# convert multiple ppts to pdf
# sp.run(["lowriter", "--convert-to", "pdf", "*.pptx"])


# convert text file to pdf
sp.run(
    ["lowriter", "--convert-to", "pdf", "sample.txt", "--outdir", "results/txt2pdf"],
)

# convert multiple text files to pdf

# sp.run(["lowriter", "--convert-to", "pdf", "*.txt"])
