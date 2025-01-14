import sys, os, struct
elf_type = None
ELF_HEADER_SIZE = lambda: 0x34 if elf_type == 1 else 0x40
E_PHNUM_OFFSET = lambda: 0x2C if elf_type == 1 else 0x38
E_TYPE_OFFSET = 0x4

PHDR_SIZE = lambda :0x20 if elf_type == 1 else 0x38
P_FILESZ_OFFSET = lambda: 0x10 if elf_type == 1 else 0x20
P_OFFSET_OFFSET = lambda: 0x4 if elf_type == 1 else 0x8
INT_LEN = lambda: 0x4 if elf_type == 1 else 0x8

def main():

	#Reading the arguments
	if len(sys.argv) != 4:
		print("USAGE: <TRUSTLET_DIR> <TRUSTLET_NAME> <OUTPUT_FILE_PATH>")
		return
	trustlet_dir = sys.argv[1]
	trustlet_name = sys.argv[2]
	output_file_path = sys.argv[3]

	#Reading the ELF header from the ".mdt" file
	mdt = open(os.path.join(trustlet_dir, "%s.mdt" % trustlet_name), "rb")
	
	_e = mdt.read(0x5)
	mdt.seek(0)
	global elf_type
	elf_type = _e[E_TYPE_OFFSET]
	if elf_type!=1 and elf_type!=2:
		exit()
	elf_header = mdt.read(ELF_HEADER_SIZE())

	print(elf_type)
	print(E_PHNUM_OFFSET())
	print(ELF_HEADER_SIZE())
	phnum = struct.unpack("<H", elf_header[E_PHNUM_OFFSET():E_PHNUM_OFFSET()+2])[0]
	print("[+] Found %d program headers" % phnum)
	
	#Reading each of the program headers and copying the relevant chunk
	output_file = open(output_file_path, 'wb')
	for i in range(0, phnum):

		#Reading the PHDR
		print("[+] Reading PHDR %d" % i)
		phdr = mdt.read(PHDR_SIZE())

		p_filesz = struct.unpack("<I" if INT_LEN()==4 else "<Q", phdr[P_FILESZ_OFFSET():P_FILESZ_OFFSET()+INT_LEN()])[0] 
		p_offset= struct.unpack("<I" if INT_LEN()==4 else "<Q", phdr[P_OFFSET_OFFSET():P_OFFSET_OFFSET()+INT_LEN()])[0] 
		print("[+] Size: 0x%08X, Offset: 0x%08X" % (p_filesz, p_offset))

		if p_filesz == 0:
			print("[+] Empty block, skipping")
			continue #There's no backing block

		#Copying out the data in the block
		block = open(os.path.join(trustlet_dir, "%s.b%02d" % (trustlet_name, i)), 'rb').read()
		output_file.seek(p_offset, 0)
		output_file.write(block)

	mdt.close()
	output_file.close()

if __name__ == "__main__":
	main()
