# Tau Core Physical Source Realization

An unnumbered technical companion that precedes the existing seed--body,
body--readout and terminal-readout packages.

**Repository:**
[`tau-core-research/tau-core-physical-source-realization-technical-paper-td0`](https://github.com/tau-core-research/tau-core-physical-source-realization-technical-paper-td0)

**Status:** conditional mathematical closure and reproducibility package;
P3 component completeness is internally closed, while global physical
source-language exhaustivity and Nature occupation remain open.

## Main claim

For a declared complete seed presentation, a source-compatible Hodge-action
completion, a two-sided source-to-base realization and an independently owned
constrained heat-trace minimum principle, one can export a typed
`BaseSeedPacket` without using terminal data. Proper finite carrier extensions
are then rejected by a strict min--max/heat-trace inequality, and the selected
positive spectral state is faithful and cyclic.

## Does not claim

- that old-bare Tau forces the constrained heat-trace minimum principle;
- that Nature realizes the declared complete seed presentation;
- that spectral minimality alone selects terminal roles, spacetime dimension,
  quantum structure, gravity or numerical constants;
- that one exact off-shell parent action is observable or uniquely selected;
- that internal closure is empirical validation.

## Included data

No observational endpoints are used. The package contains a generated proof
map, a theorem ledger, a derivation audit and a typed interface contract. It
also contains one source-frozen P3/CLP3 `CompleteSeedPresentation` candidate
and a 30-check finite audit of its Clifford algebra, cyclic record root,
support flag, ordered ports, component-local composition and wrong-family
controls. A second frozen artifact gives one nonnegative source-fidelity,
two-sided-Gram and Schur-neutral body-square action and audits its conditional
compression of P4--P7 in 23 checks.

A third artifact implements an 18-check independent-ambient P1 certificate.
For a finite physical source algebra fixed independently of the seed
candidate, with a faithful state and a frozen physical-null quotient, P1 is
equivalent to full rank of the seed-generated regular-GNS span. Missing local
relations, hidden central components and a nonfaithful-state false positive
are all detected by explicit controls.

A fourth, 21-check separator imports the independently declared pre-body
`PUSC-P1` simple source envelope rather than reusing the P3 candidate as its
own ambient. The dimensional distinction is decisive:

```text
P3/CLP3 component algebra:  Cl_7(C) tensor (C direct-sum C), dim_C = 256
pre-body PUSC envelope:      Cl_10(C) = M_32(C),             dim_C = 1024
```

Hence, if the PUSC Clifford envelope is ontic and the typed embedding is
physically owned, P3 is component-complete but fails global P1 with faithful
GNS rank ratio `256/1024 = 1/4`. If the envelope is only an auxiliary
norm/trace completion, the same local P3 packet does not determine the
physical ambient algebra. This exact fork sharpens P1 but does not decide
which branch Nature occupies. The post-body `Cl_16(C)` continuation is kept
as a downstream control and is explicitly forbidden as an upstream P1 input.

A fifth, 24-check connector audit resolves the finite algebraic part of that
fork. In one explicit 32-dimensional `Cl_10(C)` representation, the P3
algebra is the four-block algebra selected by commuting chirality and record
involutions. Two homogeneous source connectors,

```text
u = gamma_8,  v = gamma_10,  gamma_9 = -i u r,
```

give the exact dimension ladder `256 -> 512 -> 1024`: neither connector alone
fills the PUSC envelope, while both generate `M_32(C)`. A single nonnegative
connector-defect action enforces their Clifford relations and rejects absent,
rescaled and wrong-grading controls. This is a conditional ontic completion,
not Nature selection: the current P3 packet does not supply the typed `u,v`
domain. Because `M_32(C)` is simple, its missing directions also cannot be
removed by a nontrivial star-ideal quotient to `M_8(C)^{oplus 4}`.

A sixth, 31-check record--Clifford audit removes the artificial need to own
`u` and `v` as two separate primitives. Conditional on one even,
trace-preserving embedding of the existing binary record algebra into the
even Clifford algebra of the three-dimensional PUSC complement, the record
involution has adjoint spectrum `(-1,-1,+1)`. Its two-dimensional minus plane
and one-dimensional plus line reproduce the connector frame; rotations and
signs are gauge, and every audited frame still generates `Cl_10(C)`. Two
explicit controls preserve the same local P3/record four-block data while
failing global parity or complement preservation. Therefore the present
source does not yet derive the embedding. The physical blocker is narrower:
one graded record--Clifford incidence and its occupation, not two independent
connector variables.

A seventh, 17-check landing audit sharpens this once more. The even relative
commutant of the P3 `Cl_7(C)` algebra is `Cl_3(C)^even ~= M_2(C)`. A unital,
trace-preserving star embedding of the equal-weight binary record algebra
into this codomain automatically gives rank-one record projectors, preserves
the three-dimensional vector complement and lies in one `Spin(3)` conjugacy
orbit. Thus there is no physical embedding angle and the earlier explicit
complement-preservation premise is redundant. The present Schur-neutral
PUSC--record action still does not force this result: it has no
record-to-Clifford map variable and no even-relative-commutant cross residual.
The exact remaining datum is physical occupation of the landing class, not
selection of one representative map.

An eighth, 18-check source-completion audit proves that this remaining gap is
not already hidden in the common action. An internal record landing and an
external tensor-record realization have identical current PUSC and
Frobenius-record reducts, so the landing is not entailed. Conditional on an
in-envelope record image, the single endpoint-blind residual

```text
rho_IGL(R) = direct_sum([R,gamma_1],...,[R,gamma_7],[R,Gamma_10])
```

has zero set exactly equal to the even-relative-commutant landing manifold.
An odd-twist control passes role locality but fails evenness; an even
role-mixing control passes evenness but fails role locality. Thus both pieces
are necessary. This is a minimal conditional completion, not a derivation
that the physical source owns the in-envelope record domain or that Nature
occupies its zero set.

The P3/CLP3 file exports only a `BaseSeedPacketCandidate`. Its ownership
certificate explicitly forbids promotion to a physical `BaseSeedPacket` until
the missing Nature-selection premises are independently supplied.

The single-action result does not self-certify P1: the action can enforce a
supplied complete residual language but cannot prove that its own language is
physically exhaustive. Thus P4--P7 cease to be four independent mathematical
choices inside the candidate, while physical source-language ownership and
Nature occupation remain open.

The P3/CLP3 regular-GNS control has rank 256 on its declared
256-dimensional component ambient, but this is not promoted to a global
physical P1 certificate. Against the independent pre-body PUSC envelope the
rank is `256/1024`, conditional on the envelope-ontic interpretation and a
physical typed embedding.

The exact ownership and dependency split is recorded in
[`DEPENDENCY_LEDGER.md`](DEPENDENCY_LEDGER.md). The provenance and data scope
are recorded in [`DATA_NOTICE.md`](DATA_NOTICE.md).

## Reproduce

```bash
git clone https://github.com/tau-core-research/tau-core-physical-source-realization-technical-paper-td0.git
cd tau-core-physical-source-realization-technical-paper-td0
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

The command audits the finite controls, regenerates the figure, compiles the
PDF with `tectonic`, builds the source-only arXiv archive and runs the tests.
No checkout of the central theory repository is required.

## arXiv source package

`arxiv_submission_source.zip` contains only the LaTeX source, bibliography and
paper figure. It excludes the compiled PDF and build intermediates.

## Scope

This is a conditional physical-source realization calculus and a precise
non-entailment boundary. Foundation Paper IV and the parent-theory hub retain
ownership of unrestricted physical parent selection. This companion creates
no new Roman numeral.
