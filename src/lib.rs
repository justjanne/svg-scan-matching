use pyo3::prelude::*;

#[pymodule]
mod fcmconv {
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;
    use pyo3::types::PyBytes;
    use std::ops::Deref;

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject)]
    struct FcmFile {
        pub header: Py<FileHeader>,
        pub cut: Py<CutData>,
        pub pieces: Vec<Py<Piece>>,
    }

    #[pymethods]
    impl FcmFile {
        #[new]
        fn new(header: Py<FileHeader>, cut: Py<CutData>, pieces: Vec<Py<Piece>>) -> FcmFile {
            FcmFile {
                header,
                cut,
                pieces,
            }
        }

        fn write(&self, file: String, py: Python<'_>) -> PyResult<Option<String>> {
            if let Err(err) = self.to_model(py).to_file(file) {
                Ok(Some(err.to_string()))
            } else {
                Ok(None)
            }
        }

        #[staticmethod]
        fn read(file: String, py: Python<'_>) -> Option<Py<FcmFile>> {
            fcmlib::FcmFile::from_file(file)
                .ok()
                .and_then(|it| FcmFile::from_model(&it, py).ok())
        }
    }

    impl FcmFile {
        fn to_model(&self, py: Python<'_>) -> fcmlib::FcmFile {
            fcmlib::FcmFile {
                file_header: self.header.borrow(py).to_model(py),
                cut_data: self.cut.borrow(py).to_model(py),
                piece_table: fcmlib::PieceTable {
                    pieces: self
                        .pieces
                        .iter()
                        .enumerate()
                        .map(|(index, piece)| (index as u16, piece.borrow(py).to_model(py)))
                        .collect(),
                },
            }
        }

        fn from_model(model: &fcmlib::FcmFile, py: Python<'_>) -> PyResult<Py<FcmFile>> {
            Py::new(
                py,
                FcmFile {
                    header: FileHeader::from_model(&model.file_header, py)?,
                    cut: CutData::from_model(&model.cut_data, py)?,
                    pieces: model
                        .piece_table
                        .pieces
                        .iter()
                        .map(|(_, it)| Piece::from_model(it, py))
                        .collect::<PyResult<Vec<Py<Piece>>>>()?,
                },
            )
        }
    }

    impl std::fmt::Display for FcmFile {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let header = self.header.borrow(py).to_string();
                let cut = self.cut.borrow(py).to_string();
                let pieces = self
                    .pieces
                    .iter()
                    .map(|it| it.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                write!(
                    f,
                    "FcmFile(header={}, cut={}, pieces=[{}])",
                    header, cut, pieces
                )
            })
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct FileHeader {
        pub variant: Py<FileVariant>,
        pub version: String,
        pub content_id: u32,
        pub short_name: String,
        pub long_name: String,
        pub author_name: String,
        pub copyright: String,
        pub thumbnail_block_size_width: u8,
        pub thumbnail_block_size_height: u8,
        pub thumbnail: Py<PyBytes>,
        pub generator: Py<Generator>,
        pub print_to_cut: Option<bool>,
    }

    #[pymethods]
    impl FileHeader {
        #[new]
        fn new(
            variant: Py<FileVariant>,
            version: String,
            content_id: u32,
            short_name: String,
            long_name: String,
            author_name: String,
            copyright: String,
            thumbnail_block_size_width: u8,
            thumbnail_block_size_height: u8,
            thumbnail: Py<PyBytes>,
            generator: Py<Generator>,
            print_to_cut: Option<bool>,
        ) -> FileHeader {
            FileHeader {
                variant,
                version,
                content_id,
                short_name,
                long_name,
                author_name,
                copyright,
                thumbnail_block_size_width,
                thumbnail_block_size_height,
                thumbnail,
                generator,
                print_to_cut,
            }
        }
    }

    impl FileHeader {
        fn to_model(&self, py: Python<'_>) -> fcmlib::FileHeader {
            fcmlib::FileHeader {
                variant: self.variant.borrow(py).to_model(),
                version: self.version.clone(),
                content_id: self.content_id,
                short_name: self.short_name.clone(),
                long_name: self.long_name.clone(),
                author_name: self.author_name.clone(),
                copyright: self.copyright.clone(),
                thumbnail_block_size_width: self.thumbnail_block_size_height,
                thumbnail_block_size_height: self.thumbnail_block_size_width,
                thumbnail: self.thumbnail.as_bytes(py).to_vec(),
                generator: self.generator.borrow(py).to_model(),
                print_to_cut: self.print_to_cut,
            }
        }

        fn from_model(model: &fcmlib::FileHeader, py: Python<'_>) -> PyResult<Py<FileHeader>> {
            Py::new(
                py,
                FileHeader {
                    variant: FileVariant::from_model(&model.variant, py)?,
                    version: model.version.clone(),
                    content_id: model.content_id,
                    short_name: model.short_name.clone(),
                    long_name: model.long_name.clone(),
                    author_name: model.author_name.clone(),
                    copyright: model.copyright.clone(),
                    thumbnail_block_size_width: model.thumbnail_block_size_height,
                    thumbnail_block_size_height: model.thumbnail_block_size_width,
                    thumbnail: PyBytes::new(py, model.thumbnail.as_slice()).unbind(),
                    generator: Generator::from_model(&model.generator, py)?,
                    print_to_cut: model.print_to_cut,
                },
            )
        }
    }

    impl std::fmt::Display for FileHeader {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let variant = self.variant.borrow(py).to_string();
                let generator = self.generator.borrow(py).to_string();
                let thumbnail = self.thumbnail.as_bytes(py).len();
                let print_to_cut = self
                    .print_to_cut
                    .as_ref()
                    .map(|it| it.to_string())
                    .unwrap_or("None".to_string());

                write!(
                    f,
                    "FileHeader(variant={}, version=\"{}\", content_id={}, \
                 short_name=\"{}\", long_name=\"{}\", author_name=\"{}\", \
                 copyright=\"{}\", thumbnail_block_size_width={}, \
                 thumbnail_block_size_height={}, thumbnail=<bytes len={}>, \
                 generator={}, print_to_cut={})",
                    variant,
                    self.version,
                    self.content_id,
                    self.short_name,
                    self.long_name,
                    self.author_name,
                    self.copyright,
                    self.thumbnail_block_size_width,
                    self.thumbnail_block_size_height,
                    thumbnail,
                    generator,
                    print_to_cut
                )
            })
        }
    }

    #[pyclass(eq, str)]
    #[derive(PartialEq, Debug, Clone)]
    enum Generator {
        #[pyo3(constructor = (version))]
        App { version: u32 },
        #[pyo3(constructor = (version))]
        Web { version: u32 },
        #[pyo3(constructor = (model, version))]
        Device { model: u32, version: u32 },
    }

    impl Generator {
        fn to_model(&self) -> fcmlib::Generator {
            match self {
                Generator::App { version } => fcmlib::Generator::App(*version),
                Generator::Web { version } => fcmlib::Generator::Web(*version),
                Generator::Device { model, version } => fcmlib::Generator::Device(*model, *version),
            }
        }

        fn from_model(model: &fcmlib::Generator, py: Python<'_>) -> PyResult<Py<Generator>> {
            Py::new(
                py,
                match model {
                    fcmlib::Generator::App(version) => Generator::App { version: *version },
                    fcmlib::Generator::Web(version) => Generator::Web { version: *version },
                    fcmlib::Generator::Device(model, version) => Generator::Device {
                        model: *model,
                        version: *version,
                    },
                },
            )
        }
    }

    impl std::fmt::Display for Generator {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            match self {
                Generator::App { version } => {
                    write!(f, "Generator::App(version={})", version)
                }
                Generator::Web { version } => {
                    write!(f, "Generator::Web(version={})", version)
                }
                Generator::Device { model, version } => {
                    write!(f, "Generator::Device(model={}, version={})", model, version)
                }
            }
        }
    }

    #[pyclass(eq, eq_int, str)]
    #[derive(PartialEq, Debug, Clone)]
    enum FileVariant {
        FCM,
        VCM,
    }

    impl FileVariant {
        fn to_model(&self) -> fcmlib::FileVariant {
            match self {
                FileVariant::FCM => fcmlib::FileVariant::FCM,
                FileVariant::VCM => fcmlib::FileVariant::VCM,
            }
        }

        fn from_model(model: &fcmlib::FileVariant, py: Python<'_>) -> PyResult<Py<FileVariant>> {
            Py::new(
                py,
                match model {
                    fcmlib::FileVariant::FCM => FileVariant::FCM,
                    fcmlib::FileVariant::VCM => FileVariant::VCM,
                },
            )
        }
    }

    impl std::fmt::Display for FileVariant {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let s = match self {
                FileVariant::FCM => "FCM",
                FileVariant::VCM => "VCM",
            };

            write!(f, "{s}")
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct CutData {
        pub file_type: Py<FileType>,
        pub mat_id: u32,
        pub cut_width: u32,
        pub cut_height: u32,
        pub seam_allowance_width: u32,
        pub alignment: Option<Py<AlignmentData>>,
    }

    #[pymethods]
    impl CutData {
        #[new]
        fn new(
            file_type: Py<FileType>,
            mat_id: u32,
            cut_width: u32,
            cut_height: u32,
            seam_allowance_width: u32,
            alignment: Option<Py<AlignmentData>>,
        ) -> CutData {
            CutData {
                file_type,
                mat_id,
                cut_width,
                cut_height,
                seam_allowance_width,
                alignment,
            }
        }
    }

    impl CutData {
        fn to_model(self: &CutData, py: Python<'_>) -> fcmlib::CutData {
            fcmlib::CutData {
                file_type: self.file_type.borrow(py).to_model(),
                mat_id: self.mat_id,
                cut_width: self.cut_width,
                cut_height: self.cut_height,
                seam_allowance_width: self.seam_allowance_width,
                alignment: self.alignment.as_ref().map(|it| it.borrow(py).to_model(py)),
            }
        }

        fn from_model(model: &fcmlib::CutData, py: Python<'_>) -> PyResult<Py<CutData>> {
            let value = CutData {
                file_type: FileType::from_model(&model.file_type, py)?,
                mat_id: model.mat_id,
                cut_width: model.cut_width,
                cut_height: model.cut_height,
                seam_allowance_width: model.seam_allowance_width,
                alignment: model
                    .alignment
                    .as_ref()
                    .map(|it| AlignmentData::from_model(it, py))
                    .transpose()?,
            };
            Py::new(py, value)
        }
    }

    impl std::fmt::Display for CutData {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let file_type = self.file_type.borrow(py).to_string();

                let alignment = self
                    .alignment
                    .as_ref()
                    .map(|it| it.borrow(py).to_string())
                    .unwrap_or("None".to_string());

                write!(
                    f,
                    "CutData(file_type={}, mat_id={}, cut_width={}, cut_height={}, \
                 seam_allowance_width={}, alignment={})",
                    file_type,
                    self.mat_id,
                    self.cut_width,
                    self.cut_height,
                    self.seam_allowance_width,
                    alignment
                )
            })
        }
    }

    #[pyclass(eq, eq_int, str)]
    #[derive(PartialEq, Debug, Clone)]
    enum FileType {
        Cut,
        PrintAndCut,
    }

    impl FileType {
        fn to_model(&self) -> fcmlib::FileType {
            match self {
                FileType::Cut => fcmlib::FileType::Cut,
                FileType::PrintAndCut => fcmlib::FileType::PrintAndCut,
            }
        }

        fn from_model(model: &fcmlib::FileType, py: Python<'_>) -> PyResult<Py<FileType>> {
            Py::new(
                py,
                match model {
                    fcmlib::FileType::Cut => FileType::Cut,
                    fcmlib::FileType::PrintAndCut => FileType::PrintAndCut,
                },
            )
        }
    }

    impl std::fmt::Display for FileType {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let s = match self {
                FileType::Cut => "Cut",
                FileType::PrintAndCut => "PrintAndCut",
            };

            write!(f, "{s}")
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct AlignmentData {
        pub needed: bool,
        pub marks: Vec<Py<Point>>,
    }

    #[pymethods]
    impl AlignmentData {
        #[new]
        fn new(needed: bool, marks: Vec<Py<Point>>) -> AlignmentData {
            AlignmentData { needed, marks }
        }
    }

    impl AlignmentData {
        fn to_model(&self, py: Python<'_>) -> fcmlib::AlignmentData {
            fcmlib::AlignmentData {
                needed: self.needed,
                marks: self
                    .marks
                    .iter()
                    .map(|path| path.borrow(py).to_model())
                    .collect(),
            }
        }

        fn from_model(
            model: &fcmlib::AlignmentData,
            py: Python<'_>,
        ) -> PyResult<Py<AlignmentData>> {
            Py::new(
                py,
                AlignmentData {
                    needed: model.needed,
                    marks: model
                        .marks
                        .iter()
                        .map(|it| Point::from_model(&it, py))
                        .collect::<PyResult<Vec<Py<Point>>>>()?,
                },
            )
        }
    }

    impl std::fmt::Display for AlignmentData {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let marks = self
                    .marks
                    .iter()
                    .map(|m| m.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                write!(
                    f,
                    "AlignmentData(needed={}, marks=[{}])",
                    self.needed, marks
                )
            })
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct Piece {
        pub width: u32,
        pub height: u32,
        pub transform: Option<(f32, f32, f32, f32, f32, f32)>,
        pub expansion_limit_value: u32,
        pub reduction_limit_value: u32,
        pub restriction_flags: Vec<Py<PieceRestrictions>>,
        pub label: String,
        pub paths: Vec<Py<Path>>,
    }

    #[pymethods]
    impl Piece {
        #[new]
        fn new(
            width: u32,
            height: u32,
            transform: Option<(f32, f32, f32, f32, f32, f32)>,
            expansion_limit_value: u32,
            reduction_limit_value: u32,
            restriction_flags: Vec<Py<PieceRestrictions>>,
            label: String,
            paths: Vec<Py<Path>>,
        ) -> Piece {
            Piece {
                width,
                height,
                transform,
                expansion_limit_value,
                reduction_limit_value,
                restriction_flags,
                label,
                paths,
            }
        }
    }

    impl Piece {
        fn to_model(&self, py: Python<'_>) -> fcmlib::Piece {
            fcmlib::Piece {
                width: self.width,
                height: self.height,
                transform: self.transform,
                expansion_limit_value: self.expansion_limit_value,
                reduction_limit_value: self.reduction_limit_value,
                restriction_flags: fcmlib::PieceRestrictions::from_iter(
                    self.restriction_flags
                        .iter()
                        .map(|it| it.borrow(py).to_model()),
                ),
                label: self.label.clone(),
                paths: self
                    .paths
                    .iter()
                    .map(|path| path.borrow(py).to_model(py))
                    .collect(),
            }
        }

        fn from_model(model: &fcmlib::Piece, py: Python<'_>) -> PyResult<Py<Piece>> {
            Py::new(
                py,
                Piece {
                    width: model.width,
                    height: model.height,
                    transform: model.transform,
                    expansion_limit_value: model.expansion_limit_value,
                    reduction_limit_value: model.reduction_limit_value,
                    restriction_flags: model
                        .restriction_flags
                        .iter()
                        .map(|it| PieceRestrictions::from_model(it, py))
                        .collect::<PyResult<Vec<Py<PieceRestrictions>>>>()?,
                    label: model.label.clone(),
                    paths: model
                        .paths
                        .iter()
                        .map(|it| Path::from_model(it, py))
                        .collect::<PyResult<Vec<Py<Path>>>>()?,
                },
            )
        }
    }

    impl std::fmt::Display for Piece {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let restriction_flags = self
                    .restriction_flags
                    .iter()
                    .map(|r| r.borrow(py).to_string())
                    .collect::<Vec<_>>()
                    .join(", ");

                let transform = self
                    .transform
                    .as_ref()
                    .map(|(a, b, c, d, e, f)| format!("({}, {}, {}, {}, {}, {})", a, b, c, d, e, f))
                    .unwrap_or("None".to_string());

                let paths = self
                    .paths
                    .iter()
                    .map(|p| p.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                write!(
                    f,
                    "Piece(width={}, height={}, transform={}, \
                 expansion_limit_value={}, reduction_limit_value={}, \
                 restriction_flags=[{}], label=\"{}\", paths=[{}])",
                    self.width,
                    self.height,
                    transform,
                    self.expansion_limit_value,
                    self.reduction_limit_value,
                    restriction_flags,
                    self.label,
                    paths,
                )
            })
        }
    }

    #[pyclass(eq, eq_int, str)]
    #[derive(PartialEq, Debug, Clone)]
    enum PieceRestrictions {
        LicenseDesign,
        SeamAllowance,
        ProhibitionOfSeamAllowanceSetting,
        NoAspectRatioChangeProhibited,
        JudgeByUsingPerfectMaskAtAutoLayout,
        TestPattern,
        ProhibitionOfEdit,
        ProhibitionOfTool,
    }

    impl PieceRestrictions {
        fn to_model(&self) -> fcmlib::PieceRestrictions {
            match self {
                PieceRestrictions::LicenseDesign => fcmlib::PieceRestrictions::LICENSE_DESIGN,
                PieceRestrictions::SeamAllowance => fcmlib::PieceRestrictions::SEAM_ALLOWANCE,
                PieceRestrictions::ProhibitionOfSeamAllowanceSetting => {
                    fcmlib::PieceRestrictions::PROHIBITION_OF_SEAM_ALLOWANCE_SETTING
                }
                PieceRestrictions::NoAspectRatioChangeProhibited => {
                    fcmlib::PieceRestrictions::NO_ASPECT_RATIO_CHANGE_PROHIBITED
                }
                PieceRestrictions::JudgeByUsingPerfectMaskAtAutoLayout => {
                    fcmlib::PieceRestrictions::JUDGE_BY_USING_PERFECT_MASK_AT_AUTO_LAYOUT
                }
                PieceRestrictions::TestPattern => fcmlib::PieceRestrictions::TEST_PATTERN,
                PieceRestrictions::ProhibitionOfEdit => {
                    fcmlib::PieceRestrictions::PROHIBITION_OF_EDIT
                }
                PieceRestrictions::ProhibitionOfTool => {
                    fcmlib::PieceRestrictions::PROHIBITION_OF_TOOL
                }
            }
        }

        fn from_model(
            model: fcmlib::PieceRestrictions,
            py: Python<'_>,
        ) -> PyResult<Py<PieceRestrictions>> {
            Py::new(
                py,
                match model {
                    fcmlib::PieceRestrictions::LICENSE_DESIGN => PieceRestrictions::LicenseDesign,
                    fcmlib::PieceRestrictions::SEAM_ALLOWANCE => PieceRestrictions::SeamAllowance,
                    fcmlib::PieceRestrictions::PROHIBITION_OF_SEAM_ALLOWANCE_SETTING => {
                        PieceRestrictions::ProhibitionOfSeamAllowanceSetting
                    }
                    fcmlib::PieceRestrictions::NO_ASPECT_RATIO_CHANGE_PROHIBITED => {
                        PieceRestrictions::NoAspectRatioChangeProhibited
                    }
                    fcmlib::PieceRestrictions::JUDGE_BY_USING_PERFECT_MASK_AT_AUTO_LAYOUT => {
                        PieceRestrictions::JudgeByUsingPerfectMaskAtAutoLayout
                    }
                    fcmlib::PieceRestrictions::TEST_PATTERN => PieceRestrictions::TestPattern,
                    fcmlib::PieceRestrictions::PROHIBITION_OF_EDIT => {
                        PieceRestrictions::ProhibitionOfEdit
                    }
                    fcmlib::PieceRestrictions::PROHIBITION_OF_TOOL => {
                        PieceRestrictions::ProhibitionOfTool
                    }
                    _ => return Err(PyValueError::new_err("Invalid piece restrictions")),
                },
            )
        }
    }

    impl std::fmt::Display for PieceRestrictions {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let s = match self {
                PieceRestrictions::LicenseDesign => "LicenseDesign",
                PieceRestrictions::SeamAllowance => "SeamAllowance",
                PieceRestrictions::ProhibitionOfSeamAllowanceSetting => {
                    "ProhibitionOfSeamAllowanceSetting"
                }
                PieceRestrictions::NoAspectRatioChangeProhibited => "NoAspectRatioChangeProhibited",
                PieceRestrictions::JudgeByUsingPerfectMaskAtAutoLayout => {
                    "JudgeByUsingPerfectMaskAtAutoLayout"
                }
                PieceRestrictions::TestPattern => "TestPattern",
                PieceRestrictions::ProhibitionOfEdit => "ProhibitionOfEdit",
                PieceRestrictions::ProhibitionOfTool => "ProhibitionOfTool",
            };

            write!(f, "{s}")
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct Path {
        pub tool: Vec<Py<PathTool>>,
        pub shape: Option<Py<PathShape>>,
        pub rhinestone_diameter: Option<u32>,
        pub rhinestones: Vec<Py<Point>>,
    }

    #[pymethods]
    impl Path {
        #[new]
        fn new(
            tool: Vec<Py<PathTool>>,
            shape: Option<Py<PathShape>>,
            rhinestone_diameter: Option<u32>,
            rhinestones: Vec<Py<Point>>,
        ) -> Path {
            Path {
                tool,
                shape,
                rhinestone_diameter,
                rhinestones,
            }
        }
    }

    impl Path {
        fn to_model(&self, py: Python<'_>) -> fcmlib::Path {
            fcmlib::Path {
                tool: fcmlib::PathTool::from_iter(
                    self.tool.iter().map(|it| it.borrow(py).to_model()),
                ),
                shape: self.shape.as_ref().map(|it| it.borrow(py).to_model(py)),
                rhinestone_diameter: self.rhinestone_diameter,
                rhinestones: self
                    .rhinestones
                    .iter()
                    .map(|it| it.borrow(py).to_model())
                    .collect(),
            }
        }

        fn from_model(model: &fcmlib::Path, py: Python<'_>) -> PyResult<Py<Path>> {
            Py::new(
                py,
                Path {
                    tool: model
                        .tool
                        .iter()
                        .map(|it| PathTool::from_model(it, py))
                        .collect::<PyResult<Vec<Py<PathTool>>>>()?,
                    shape: model
                        .shape
                        .as_ref()
                        .map(|it| PathShape::from_model(it, py))
                        .transpose()?,
                    rhinestone_diameter: model.rhinestone_diameter,
                    rhinestones: model
                        .rhinestones
                        .iter()
                        .map(|it| Point::from_model(it, py))
                        .collect::<PyResult<Vec<Py<Point>>>>()?,
                },
            )
        }
    }

    impl std::fmt::Display for Path {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let tool = self
                    .tool
                    .iter()
                    .map(|t| t.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                let shape = self
                    .shape
                    .as_ref()
                    .map(|it| it.borrow(py).to_string())
                    .unwrap_or("None".to_string());

                let rhinestone_diameter = self
                    .rhinestone_diameter
                    .map(|d| d.to_string())
                    .unwrap_or("None".to_string());

                let rhinestones = self
                    .rhinestones
                    .iter()
                    .map(|p| p.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                write!(
                    f,
                    "Path(tool=[{}], shape={}, rhinestone_diameter={}, rhinestones=[{}])",
                    tool, shape, rhinestone_diameter, rhinestones
                )
            })
        }
    }

    #[pyclass(eq, eq_int, str)]
    #[derive(PartialEq, Debug, Clone)]
    enum PathTool {
        PathOpen,
        ToolCut,
        ToolDraw,
        SeamAllowance,
        ToolRhinestone,
        Fill,
        AutoAlign,
        ToolDrawOnly,
        ToolEmboss,
        ToolFoil,
        ToolPerforating,
    }

    impl PathTool {
        fn to_model(&self) -> fcmlib::PathTool {
            match self {
                PathTool::PathOpen => fcmlib::PathTool::PATH_OPEN,
                PathTool::ToolCut => fcmlib::PathTool::TOOL_CUT,
                PathTool::ToolDraw => fcmlib::PathTool::TOOL_DRAW,
                PathTool::SeamAllowance => fcmlib::PathTool::SEAM_ALLOWANCE,
                PathTool::ToolRhinestone => fcmlib::PathTool::TOOL_RHINESTONE,
                PathTool::Fill => fcmlib::PathTool::FILL,
                PathTool::AutoAlign => fcmlib::PathTool::AUTO_ALIGN,
                PathTool::ToolDrawOnly => fcmlib::PathTool::TOOL_DRAW_ONLY,
                PathTool::ToolEmboss => fcmlib::PathTool::TOOL_EMBOSS,
                PathTool::ToolFoil => fcmlib::PathTool::TOOL_FOIL,
                PathTool::ToolPerforating => fcmlib::PathTool::TOOL_PERFORATING,
            }
        }

        fn from_model(model: fcmlib::PathTool, py: Python<'_>) -> PyResult<Py<PathTool>> {
            Py::new(
                py,
                match model {
                    fcmlib::PathTool::PATH_OPEN => PathTool::PathOpen,
                    fcmlib::PathTool::TOOL_CUT => PathTool::ToolCut,
                    fcmlib::PathTool::TOOL_DRAW => PathTool::ToolDraw,
                    fcmlib::PathTool::SEAM_ALLOWANCE => PathTool::SeamAllowance,
                    fcmlib::PathTool::TOOL_RHINESTONE => PathTool::ToolRhinestone,
                    fcmlib::PathTool::FILL => PathTool::Fill,
                    fcmlib::PathTool::AUTO_ALIGN => PathTool::AutoAlign,
                    fcmlib::PathTool::TOOL_DRAW_ONLY => PathTool::ToolDrawOnly,
                    fcmlib::PathTool::TOOL_EMBOSS => PathTool::ToolEmboss,
                    fcmlib::PathTool::TOOL_FOIL => PathTool::ToolFoil,
                    fcmlib::PathTool::TOOL_PERFORATING => PathTool::ToolPerforating,
                    _ => return Err(PyValueError::new_err("Invalid piece restrictions")),
                },
            )
        }
    }

    impl std::fmt::Display for PathTool {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let s = match self {
                PathTool::PathOpen => "PathOpen",
                PathTool::ToolCut => "ToolCut",
                PathTool::ToolDraw => "ToolDraw",
                PathTool::SeamAllowance => "SeamAllowance",
                PathTool::ToolRhinestone => "ToolRhinestone",
                PathTool::Fill => "Fill",
                PathTool::AutoAlign => "AutoAlign",
                PathTool::ToolDrawOnly => "ToolDrawOnly",
                PathTool::ToolEmboss => "ToolEmboss",
                PathTool::ToolFoil => "ToolFoil",
                PathTool::ToolPerforating => "ToolPerforating",
            };

            write!(f, "{s}")
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct PathShape {
        pub start: Py<Point>,
        pub outlines: Vec<Py<Outline>>,
    }

    #[pymethods]
    impl PathShape {
        #[new]
        fn new(start: Py<Point>, outlines: Vec<Py<Outline>>) -> PathShape {
            PathShape { start, outlines }
        }
    }

    impl PathShape {
        fn to_model(&self, py: Python<'_>) -> fcmlib::PathShape {
            fcmlib::PathShape {
                start: self.start.borrow(py).to_model(),
                outlines: self
                    .outlines
                    .iter()
                    .map(|it| it.borrow(py).to_model(py))
                    .collect(),
            }
        }

        fn from_model(model: &fcmlib::PathShape, py: Python<'_>) -> PyResult<Py<PathShape>> {
            Py::new(
                py,
                PathShape {
                    start: Point::from_model(&model.start, py)?,
                    outlines: model
                        .outlines
                        .iter()
                        .map(|it| Outline::from_model(it, py))
                        .collect::<PyResult<Vec<Py<Outline>>>>()?,
                },
            )
        }
    }

    impl std::fmt::Display for PathShape {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let start = self.start.borrow(py);

                let outlines = self
                    .outlines
                    .iter()
                    .map(|it| it.borrow(py).to_string())
                    .collect::<Vec<String>>()
                    .join(", ");

                write!(
                    f,
                    "PathShape(start={}, outlines=[{}])",
                    start.deref(),
                    outlines
                )
            })
        }
    }

    #[pyclass(str)]
    #[derive(Debug)]
    enum Outline {
        #[pyo3(constructor = (segments))]
        Line { segments: Vec<Py<Point>> },
        #[pyo3(constructor = (segments))]
        Bezier { segments: Vec<Py<Segment>> },
    }

    impl Outline {
        fn to_model(&self, py: Python<'_>) -> fcmlib::Outline {
            match self {
                Outline::Line { segments } => fcmlib::Outline::Line(
                    segments
                        .iter()
                        .map(|it| fcmlib::SegmentLine {
                            end: it.borrow(py).to_model(),
                        })
                        .collect(),
                ),
                Outline::Bezier { segments } => fcmlib::Outline::Bezier(
                    segments
                        .iter()
                        .map(|it| it.borrow(py).to_model(py))
                        .collect(),
                ),
            }
        }

        fn from_model(model: &fcmlib::Outline, py: Python<'_>) -> PyResult<Py<Outline>> {
            Py::new(
                py,
                match model {
                    fcmlib::Outline::Line(segments) => Outline::Line {
                        segments: segments
                            .iter()
                            .map(|it| Point::from_model(&it.end, py))
                            .collect::<PyResult<Vec<Py<Point>>>>()?,
                    },
                    fcmlib::Outline::Bezier(segments) => Outline::Bezier {
                        segments: segments
                            .iter()
                            .map(|it| Segment::from_model(it, py))
                            .collect::<PyResult<Vec<Py<Segment>>>>()?,
                    },
                },
            )
        }
    }

    impl std::fmt::Display for Outline {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| match self {
                Outline::Line { segments } => {
                    write!(
                        f,
                        "Outline.Line(segments=[{}])",
                        segments
                            .iter()
                            .map(|it| it.borrow(py).to_string())
                            .collect::<Vec<String>>()
                            .join(", ")
                    )
                }
                Outline::Bezier { segments } => {
                    write!(
                        f,
                        "Outline.Bezier(segments={})",
                        segments
                            .iter()
                            .map(|it| it.borrow(py).to_string())
                            .collect::<Vec<String>>()
                            .join(", ")
                    )
                }
            })
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, Debug)]
    struct Segment {
        pub control1: Py<Point>,
        pub control2: Py<Point>,
        pub end: Py<Point>,
    }

    #[pymethods]
    impl Segment {
        #[new]
        fn new(control1: Py<Point>, control2: Py<Point>, end: Py<Point>) -> Segment {
            Segment {
                control1,
                control2,
                end,
            }
        }
    }

    impl Segment {
        fn to_model(&self, py: Python<'_>) -> fcmlib::SegmentBezier {
            fcmlib::SegmentBezier {
                control1: self.control1.borrow(py).to_model(),
                control2: self.control2.borrow(py).to_model(),
                end: self.end.borrow(py).to_model(),
            }
        }

        fn from_model(model: &fcmlib::SegmentBezier, py: Python<'_>) -> PyResult<Py<Segment>> {
            Py::new(
                py,
                Segment {
                    control1: Point::from_model(&model.control1, py)?,
                    control2: Point::from_model(&model.control2, py)?,
                    end: Point::from_model(&model.end, py)?,
                },
            )
        }
    }

    impl std::fmt::Display for Segment {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            Python::attach(|py| {
                let c1 = self.control1.borrow(py);
                let c2 = self.control2.borrow(py);
                let end = self.end.borrow(py);

                write!(
                    f,
                    "Segment(control1={}, control2={}, end={})",
                    c1.deref(),
                    c2.deref(),
                    end.deref()
                )
            })
        }
    }

    #[pyclass(subclass, get_all, immutable_type, str)]
    #[derive(FromPyObject, PartialEq, Eq, Debug)]
    struct Point {
        pub x: i32,
        pub y: i32,
    }

    #[pymethods]
    impl Point {
        #[new]
        fn new(x: i32, y: i32) -> Point {
            Point { x, y }
        }
    }

    impl Point {
        fn to_model(&self) -> fcmlib::Point {
            fcmlib::Point {
                x: self.x,
                y: self.y,
            }
        }

        fn from_model(model: &fcmlib::Point, py: Python<'_>) -> PyResult<Py<Point>> {
            Py::new(
                py,
                Point {
                    x: model.x,
                    y: model.y,
                },
            )
        }
    }

    impl std::fmt::Display for Point {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "Point(x={}, y={})", self.x, self.y)
        }
    }
}
