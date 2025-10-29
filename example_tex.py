from manim import *
import numpy as np

class ProductRuleDiagram(Scene):
    def construct(self):
        df = 0.4
        dg = 0.2
        rect_kwargs = {
            "stroke_width" : 0,
            "fill_color" : BLUE,
            "fill_opacity" : 0.6,
        }

        rect = Rectangle(width = 4, height = 3, **rect_kwargs)
        rect.shift(DOWN)
        df_rect = Rectangle(
            height = rect.get_height(),
            width = df,
            **rect_kwargs
        )
        dg_rect = Rectangle(
            height = dg,
            width = rect.get_width(),
            **rect_kwargs
        )
        corner_rect = Rectangle(
            height = dg, 
            width = df,
            **rect_kwargs
        )
        d_rects = VGroup(df_rect, dg_rect, corner_rect)
        for d_rect, direction in zip(d_rects, [RIGHT, DOWN, RIGHT+DOWN]):
            d_rect.next_to(rect, direction, buff = 0)
            d_rect.set_fill(YELLOW, 0.75)

        corner_pairs = [
            (DOWN+RIGHT, UP+RIGHT),
            (DOWN+RIGHT, DOWN+LEFT),
            (DOWN+RIGHT, DOWN+RIGHT),
        ]
        for d_rect, corner_pair in zip(d_rects, corner_pairs):
            line = Line(*[
                rect.get_corner(corner)
                for corner in corner_pair
            ])
            d_rect.line = d_rect.copy().replace(line, stretch = True)
            d_rect.line.set_color(d_rect.get_color())

        f_brace = Brace(rect, UP)
        g_brace = Brace(rect, LEFT)
        df_brace = Brace(df_rect, UP)
        dg_brace = Brace(dg_rect, LEFT)

        # Create labels explicitly (Brace.get_text may vary across manim versions)
        f_label = MathTex("f")
        g_label = MathTex("g")
        df_label = MathTex("df")
        dg_label = MathTex("dg")
        # position labels relative to their braces
        f_label.next_to(f_brace, UP)
        g_label.next_to(g_brace, LEFT)
        df_label.next_to(df_brace, UP)
        dg_label.next_to(dg_brace, LEFT)

        VGroup(f_label, df_label).set_color(GREEN)
        VGroup(g_label, dg_label).set_color(RED)

        f_label.generate_target()
        g_label.generate_target()
        fg_group = VGroup(f_label.target, g_label.target)
        fg_group.generate_target()
        fg_group.target.arrange(RIGHT, buff = SMALL_BUFF)
        fg_group.target.move_to(rect.get_center())

        for mob in (df_brace, df_label, dg_brace, dg_label):
            mob.save_state()
            # scale down around the mob's center (previous code passed a vector
            # into get_corner which is not appropriate)
            mob.scale(0.01, about_point = mob.get_center())

        self.add(rect)
        self.play(
            GrowFromCenter(f_brace),
            GrowFromCenter(g_brace),
            Write(f_label),
            Write(g_label),
        )
        self.play(MoveToTarget(fg_group))
        self.play(*[
            Restore(mob)
            for mob in (df_brace, df_label, dg_brace, dg_label)
        ] + [
            ReplacementTransform(d_rect.line, d_rect)
            for d_rect in d_rects
        ])
        self.wait()
        self.play(
            d_rects.animate.space_out_submobjects(1.2),
            MaintainPositionRelativeTo(
                VGroup(df_brace, df_label),
                df_rect
            ),
            MaintainPositionRelativeTo(
                VGroup(dg_brace, dg_label),
                dg_rect
            ),
        )
        self.wait()

        # Use MathTex and ensure \cdot is followed by an empty group to avoid
        # collapsing with the next token (LaTeX: avoid \cdotdg -> undefined control sequence)
        deriv = MathTex(
            "d(", "fg", ")", "=", 
            "f", "\\cdot{}", "dg", "+", "g", "\\cdot{}", "df"
        )
        deriv.to_edge(UP)
        alpha_iter = iter(np.linspace(0, 0.5, 5))
        anims = []
        for mob, tex in [
            (fg_group, "fg"),
            (f_label, "f"),
            (dg_label, "dg"),
            (g_label, "g"),
            (df_label, "df"),
        ]:
            alpha = next(alpha_iter)
            copy = mob.copy()
            # add the copy so it's visible, then animate the copy to the target part
            self.add(copy)
            # manim 0.19: Tex.get_part_by_tex may not be available consistently,
            # so map parts by index based on how `deriv` was constructed above.
            part_map = {
                "fg": deriv[1],
                "f": deriv[4],
                "dg": deriv[6],
                "g": deriv[8],
                "df": deriv[10],
            }
            target = part_map[tex]
            anims.append(
                ApplyMethod(
                    copy.move_to,
                    target,
                    rate_func = squish_rate_func(smooth, alpha, alpha+0.5)
                )
            )
        self.play(*anims, run_time = 3)
        self.wait()