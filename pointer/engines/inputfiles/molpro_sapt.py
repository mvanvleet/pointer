sapt_pbe0_ct_template='''***, 
!job computes, at a DFT-SAPT level of theory (pbe0/AVTZ+midbond) the
!interaction energy between monomers. eint is calculated as the
!difference between the dimer and monomers' energy.
!
!This template utilizes density fitting.
!
!Need to change the following before using template:
!   *Change dummy atom labels on monomers a and b for both dhf and sapt calc
!   *Update HOMO and IP for each monomer
!   *(Monomer names)
!   *Monomer/dimer charges
!May need to also change the following:
!   *Memory limits


gdirect; gthresh,energy=1.d-8,orbital=1.d-8,grid=1.d-8
symmetry,nosym
orient,noorient
memory,{memory},m

include, AVTZ.mbas

nosym;noorient;angstrom;
geometry={{
{geometry} }}


!sapt files
cd=2000.2
ca=2101.2
cb=2102.2

!=========delta(HF) contribution for higher order interaction terms====
    !dimer
    dummy,Be
    charge={qdimer}
{{df-hf,basis=jkfit,locorb=0}}
edm=energy

    !monomer A, {mona}
    dummy, Be, {imonb}
	charge={qmona}
{{df-hf,basis=jkfit,locorb=0; save,$ca}}
ema=energy
{{sapt;monomerA}}

	!monomer B, {monb}
    dummy, Be, {imona}
	charge={qmonb}
{{df-hf,basis=jkfit,locorb=0; save,$cb}}
emb=energy
{{sapt;monomerB}}

!interaction contributions
{{sapt,Sinf=1,SAPT_LEVEL=2;intermol,ca=$ca,cb=$cb,icpks=1,fitlevel=3
dfit,basis_coul=jkfit,basis_exch=jkfit,basis_mp2=mp2fit,cfit_scf=3}}

!calculate high-order terms by subtracting 1st+2nd order energies
eint_hf=(edm-ema-emb)*1000 mH
delta_hf=eint_hf-e1pol-e1ex-e2ind-e2exind

    data,truncate,$cd,$ca,$cb



!=========DFT-SAPT at second order intermol. perturbation theory====
!sapt files
ca=2103.2
cb=2104.2

!asymptotic correction data calcluated in /home/mvanvleet/data_reference/sapt_monomer_data/ips/
	!shifts for asymptotic correction to xc potential (in Ha)
	shift_mona = {acshift_mona}	!shift for bulk xc potential
	shift_monb = {acshift_monb} !shift for bulk xc potential

	dfit,basis_coul=jkfit,basis_exch=jkfit

    !monomer A, {mona}
    dummy, Be, {imonb}
	charge={qmona}
{{df-ks,pbex,pw91c,lhf,basis=jkfit; dftfac,0.75,1.0,0.25; asymp,shift_mona; save,$ca}}
{{sapt;monomerA}}

	!monomer B, {monb}
    dummy, Be, {imona}
	charge={qmonb}
{{df-ks,pbex,pw91c,lhf,basis=jkfit; dftfac,0.75,1.0,0.25; start,atdens; asymp,shift_monb; save,$cb}}
{{sapt;monomerB}}

!interaction contributions
{{sapt,Sinf=1,SAPT_LEVEL=3;intermol,ca=$ca,cb=$cb,icpks=0,fitlevel=3,nlexfac=0.0
dfit,basis_coul=jkfit,basis_exch=jkfit,basis_mp2=mp2fit,cfit_scf=3}}
index=E2exind
eIND1=e2ind+e2exind

	!add high-order approximation to obtain the total interaction energy
eint_dftsapt=e12tot+delta_hf

	elst=E1pol;  exch=E1ex
	ind=E2ind;   exind=E2exind
	disp=E2disp; exdisp=E2exdisp
	etot=eint_dftsapt

	data,truncate,$ca

!=========Charge Transfer Calculation, perform LPBE0AC calculation for regSAPT
    !monomer A, {mona}
    dummy, Be, {imonb}
	charge={qmona}
vreg,alpha=3d0,nq=1
{{df-ks,pbex,pw91c,lhf,basis=jkfit; dftfac,0.75,1.0,0.25; asymp,shift_mona; save,$ca}}
{{sapt;monomerA}}

	!monomer B, {monb}
    dummy, Be, {imona}
	charge={qmonb}
vreg,alpha=3d0,nq=1
{{df-ks,pbex,pw91c,lhf,basis=jkfit; dftfac,0.75,1.0,0.25; start,atdens; asymp,shift_monb; save,$cb}}
{{sapt;monomerB}}

!interaction contributions for regSAPT
{{sapt,Sinf=1,SAPT_LEVEL=2;intermol,ca=$ca,cb=$cb,icpks=0,fitlevel=3,nlexfac=0.0
dfit,basis_coul=jkfit,basis_exch=jkfit,basis_mp2=mp2fit,cfit_scf=3}}
eIND2=e2ind+e2exind

eCT=eIND1-eIND2
epol=eIND2
'''

avtz_ip_template = '''***, Ionization Energy

memory,{memory},m

basis=avtz

nosym;noorient;angstrom

geometry={{
{geometry} }}

charge={charge}
{{rks,pbe0}}
e_atom=energy

charge={ion_charge}
{{ks,pbe0}}
e_ion=energy

e_ionization=e_ion-e_atom'''
