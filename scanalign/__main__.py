import base64
import os

from scanalign.fcmconv import *

if __name__ == "__main__":
    model = FcmFile(
        header=FileHeader(
            variant=FileVariant.FCM,
            version="0100",
            content_id=400000001,
            short_name="yfoxd79mua",
            long_name="yfoxd79mua",
            author_name=" ",
            copyright=" ",
            thumbnail_block_size_width=3,
            thumbnail_block_size_height=3,
            thumbnail=base64.standard_b64decode(
                """
                Qk3uBAAAAAAAAD4AAAAoAAAAXAAAAGQAAAABAAEAAAAAAAAAAADEDgAAxA4AAAIAAAACAAAAAAAA
                //////////////////////D///////////////D///////////////D///////////////D/////
                //////////D///////////////D///////////////D///////////////D///////////////D/
                //////////////D///////////////D///////////////D///////////////D/////////////
                //D///////////////D///////////////D///////////////D///////////////D/////////
                //////D///////////////D///////////////D///////////////D///////////////D/////
                //////////D///////////////D///////////////D///////////////D///////////////D/
                //////////////D///////////////D///////////////D///////////////D/////////////
                //D///////////////D///////////////D///////////////D///////////////D/////////
                //////D///////////////D///////////////D///////////////D///////////////D/////
                //////////D///////////////D///////////////D///////////////D///////////////D/
                //////////////D///////////////D///////////////D///////////////D/////////////
                //D///////////////D///////////////D///////////////D///////////////D/////////
                //////D///////////////D///////////////D///////////////D///////////////D/////
                //////////D///////////////D///////////////D///////////////D///////////////D/
                //////////////DgAAAB//////////DAAAAB//////////Df///9//////////Df///9////////
                //Df///9//////////Df///9//////////Df///9//////////Df///9//////////Df///9////
                //////Df///9//////////Df///9//////////Df///9//////////Df///9//////////Df///9
                //////////Df///9//////////Df///9//////////Df///9//////////Df///9//////////Df
                ///9//////////Df///9//////////Df///9//////////Df///9//////////Df///9////////
                //Df///9//////////Df///9//////////Df///9//////////Df///9//////////Df///9////
                //////Df///9//////////DgAAAB//////////D///////////////D///////////////D/////
                //////////A=
                """
            ),
            generator=Generator.Web(version=200),
            print_to_cut=None,
        ),
        cut=CutData(
            file_type=FileType.Cut,
            mat_id=0,
            cut_width=29667,
            cut_height=29880,
            seam_allowance_width=2000,
            alignment=None,
        ),
        pieces=[
            Piece(
                width=9999,
                height=9999,
                transform=(1.0, 0.0, 0.0, 1.0, 5263.5, 5263.5),
                expansion_limit_value=0,
                reduction_limit_value=0,
                restriction_flags=[PieceRestrictions.ProhibitionOfSeamAllowanceSetting],
                label="A01",
                paths=[
                    Path(
                        tool=[PathTool.ToolCut],
                        shape=PathShape(
                            start=Point(5001, 5001),
                            outlines=[
                                Outline.Line(
                                    segments=[
                                        Point(-4998, 5001),
                                        Point(-4998, -4998),
                                        Point(5001, -4998),
                                        Point(5001, 5001),
                                    ],
                                ),
                            ],
                        ),
                        rhinestone_diameter=63,
                        rhinestones=[],
                    ),
                ],
            ),
            Piece(
                width=9999,
                height=9999,
                transform=(1.0, 0.0, 0.0, 1.0, 15263.5, 15263.5),
                expansion_limit_value=0,
                reduction_limit_value=0,
                restriction_flags=[PieceRestrictions.ProhibitionOfSeamAllowanceSetting],
                label="A02",
                paths=[
                    Path(
                        tool=[PathTool.ToolDraw, PathTool.ToolDrawOnly],
                        shape=PathShape(
                            start=Point(5001, 5001),
                            outlines=[
                                Outline.Line(
                                    segments=[
                                        Point(-4998, 5001),
                                        Point(-4998, -4998),
                                        Point(5001, -4998),
                                        Point(5001, 5001),
                                    ],
                                ),
                            ],
                        ),
                        rhinestone_diameter=63,
                        rhinestones=[],
                    ),
                ],
            ),
        ],
    )
    os.makedirs("build/test", exist_ok=True)
    print(model.write("build/test/test.fcm"))
