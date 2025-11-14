use pyo3::prelude::*;

#[pymodule]
mod fcmconv {
    use pyo3::prelude::*;
    use pyo3::types::PyBytes;

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(eq)]
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
    }

    #[pyclass(eq, eq_int)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(eq, eq_int)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(eq, eq_int)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(eq, eq_int)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }

    #[pyclass(subclass, get_all, immutable_type)]
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
    }
}
