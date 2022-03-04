# Analyze

This is the part considering analysis of captured side-channel traces.
During the last decades hundreds of papers where published covering all aspects of side-channel analysis.
If we are looking for tools and libraries which really can handle traces and perform analysis we will discover that there only a few of them.
In a nutshell: Many formulas, little code.

Two interesting ones to look at are: ChipWhisperer and lascar.

## Used tools and libraries

### ChipWhisperer

ChipWhisperer aims primarily educational purposes. Thus, most methods and computations could be programmed more efficient but maybe less readable.
SecureC tries to close a part of that gap by providing efficient computations but focusing on descriptive visualizations.

### Lascar

blabla

## Scope of analysis

As already stated in the introduction, our victim is an AES SBOX-lookup.
Traditionally, an SCA-attacker has done a good job when she/he can reveal the secret key by observing cryptographic computations.
What if we have to do some side-channel resistant coding? How can we assess that the implementation is secure enough?

### Key recovering

Following the traditional sport of the attacker we can try to find out the secret key.
This will be done using different methods described in their individual applications.

### Leakage assessment

It is often not necessary to recover the entire secret key.
If an attacker can mount multiple attacks she/he might use side-channel analysis to recover _some information_ of the secret and uses different methods to recover the secret or break the system.
Hence, it is necessary for us to provide not only sufficient security so that a key cannot be recovered but also assessing every _leakage_.

Leakage, in general, can be defined as the amount of information about the secret which can be gathered by analysis.
If no information is obtained, no key can be recovered.

## Structure

Each SCA method is demonstrated in two files: One containing pure Python code and one Jupyter-Notebook.
The first one aims to be used later e.g. in a CI environment.
Whereas the latter one describes the method and focuses on visualization.