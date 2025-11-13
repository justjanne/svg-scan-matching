use pyo3::prelude::*;

#[pymodule]
mod fcmconv {
    use fcmlib::Generator::App;
    use fcmlib::*;
    use pyo3::prelude::*;

    #[pyfunction]
    fn to_file() -> PyResult<Option<String>> {
        let x = FcmFile {
            file_header: FileHeader {
                variant: FileVariant::FCM,
                version: "0100".to_string(),
                content_id: 400000002,
                short_name: "".to_string(),
                long_name: " ".to_string(),
                author_name: " ".to_string(),
                copyright: " ".to_string(),
                thumbnail_block_size_width: 3,
                thumbnail_block_size_height: 3,
                thumbnail: vec![],
                generator: App(0),
                print_to_cut: None,
            },
            cut_data: CutData {
                file_type: FileType::Cut,
                mat_id: 0,
                cut_width: 29667,
                cut_height: 29880,
                seam_allowance_width: 2000,
                alignment: None,
            },
            piece_table: PieceTable {
                pieces: vec![(
                    0,
                    Piece {
                        width: 21000,
                        height: 29700,
                        transform: Some((1.0, 0.0, 0.0, 1.0, 0.0, 0.0)),
                        expansion_limit_value: 0,
                        reduction_limit_value: 0,
                        restriction_flags: PieceRestrictions::PROHIBITION_OF_SEAM_ALLOWANCE_SETTING,
                        label: "".to_string(),
                        paths: vec![Path {
                            tool: PathTool::TOOL_CUT,
                            shape: Some(PathShape {
                                start: Point { x: 0, y: 0 },
                                outlines: vec![Outline::Bezier(vec![SegmentBezier {
                                    control1: Point { x: 0, y: 0 },
                                    control2: Point { x: 0, y: 0 },
                                    end: Point { x: 0, y: 0 },
                                }])],
                            }),
                            rhinestone_diameter: None,
                            rhinestones: vec![],
                        }],
                    },
                )],
            },
        };
        if let Err(err) = x.to_file("build/test/test.fcm") {
            Ok(Some(err.to_string()))
        } else {
            Ok(None)
        }
    }
}
