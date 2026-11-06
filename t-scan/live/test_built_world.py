"""Manifest v3: classified pieces, layered cells, role validation, and what the model is shown of a built world."""
import copy,glob,json,tempfile,unittest
from pathlib import Path
from grid_world import GridWorld
from grid_context import coordinate_world
from world_manifest import validate_manifest,ROLES

def piece(prototype,name,role,blocks):return dict(prototype=prototype,name=name,role=role,blocks=blocks)
CATALOG=[piece('t_floor','Test floor','floor',False),piece('t_wall','Test wall','wall',True),piece('t_barrel','Test barrel','obstacle',True),piece('t_door','Test door','structure',True),
         piece('t_arch','Test arch','structure',False),piece('t_spikes','Test spike trap','hazard',False),piece('t_flowers','Test flowers','decor',False)]
def placement(i,prototype,col,row,yaw=0):return dict(id=i,prototype=prototype,col=col,row=row,yaw=yaw)

def built():
    return dict(schema='meadow-world-v3',world_id='steve_grid_v1',revision=3,columns=15,rows=15,spawn=dict(col=8,row=8),
        landmarks=[dict(id='target_blue',name='Blue flag',kind='flag',color='blue',col=15,row=15,occupiable=True)],
        floors=['t_floor']*225,
        obstacles=[placement('w1','t_wall',9,8),placement('w2','t_wall',9,9),placement('b1','t_barrel',7,8),placement('d1','t_door',8,9)],
        props=[placement('h1','t_spikes',8,7),placement('f1','t_flowers',3,3),placement('a1','t_arch',8,10)],
        catalog=copy.deepcopy(CATALOG))

class RoleRules(unittest.TestCase):
    def test_a_correctly_classified_world_validates_and_hashes_stably(self):
        first,digest=validate_manifest(built());again,digest2=validate_manifest(built())
        self.assertEqual(digest,digest2);self.assertEqual([o['id'] for o in first['obstacles']],['b1','d1','w1','w2'])
        shuffled=built();shuffled['obstacles'].reverse();self.assertEqual(validate_manifest(shuffled)[1],digest)

    def rejects(self,mutate,fragment):
        value=built();mutate(value)
        with self.assertRaises(ValueError) as caught:validate_manifest(value)
        self.assertIn(fragment,str(caught.exception));return str(caught.exception)

    def test_a_floor_cannot_be_placed_as_a_wall(self):
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_floor',2,2)),'floor and cannot be placed there')

    def test_a_wall_cannot_be_decor_and_a_barrel_cannot_be_a_floor(self):
        self.rejects(lambda m:m['props'].append(placement('x','t_wall',2,2)),'cannot be placed there')
        def swap(m):m['floors'][0]='t_barrel'
        self.rejects(swap,'not a floor piece')

    def test_hazards_and_decor_cannot_block(self):
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_spikes',2,2)),'cannot be placed there')
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_flowers',2,2)),'cannot be placed there')

    def test_the_catalog_cannot_misstate_blocking_for_a_role(self):
        def lying_wall(m):next(c for c in m['catalog'] if c['prototype']=='t_wall')['blocks']=False
        self.rejects(lying_wall,'is a wall so it must block')
        def lying_floor(m):next(c for c in m['catalog'] if c['prototype']=='t_floor')['blocks']=True
        self.rejects(lying_floor,'is a floor so it cannot block')
        def lying_hazard(m):next(c for c in m['catalog'] if c['prototype']=='t_spikes')['blocks']=True
        self.rejects(lying_hazard,'cannot block')

    def test_structures_may_block_or_not_and_land_in_the_matching_list(self):
        self.rejects(lambda m:m['props'].append(placement('x','t_door',2,2)),'cannot be placed there')
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_arch',2,2)),'cannot be placed there')

    def test_actors_are_reserved_and_not_placeable_yet(self):
        def actor(m):m['catalog'].append(piece('t_slime','Slime','actor',True));m['obstacles'].append(placement('x','t_slime',2,2))
        self.rejects(actor,'not a placeable role')

    def test_unknown_roles_and_bad_fields_are_rejected(self):
        self.rejects(lambda m:m['catalog'][0].update(role='scenery'),'not a placeable role')
        self.rejects(lambda m:m['catalog'][0].update(extra=1),'Invalid catalog entry fields')
        self.rejects(lambda m:m['obstacles'][0].update(yaw=45),'yaw')
        self.rejects(lambda m:m['obstacles'][0].update(prototype='nowhere'),'not in the catalog')
        self.rejects(lambda m:m.update(floors=['t_floor']*224),'one floor piece for each')

    def test_the_catalog_lists_exactly_the_pieces_in_use(self):
        self.rejects(lambda m:m['catalog'].append(piece('t_extra','Unused','decor',False)),'unused: t_extra')
        def drop(m):m['catalog'][:]=[c for c in m['catalog'] if c['prototype']!='t_flowers']
        self.rejects(drop,'not in the catalog')

    def test_cell_conflicts(self):
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_wall',9,8)),'overlaps')
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_wall',8,8)),'spawn')
        self.rejects(lambda m:m['obstacles'].append(placement('x','t_wall',15,15)),'landmark')
        self.rejects(lambda m:m['props'].append(placement('x','t_flowers',9,8)),'sits inside blocking')
        self.rejects(lambda m:m['props'].append(placement('x','t_spikes',8,8)),'spawn or a landmark')
        self.rejects(lambda m:m['props'].append(placement('w1','t_flowers',2,2)),'unique')

    def test_every_landmark_must_be_reachable_from_the_spawn(self):
        def wall_in(m):m['obstacles']+=[placement('r%d'%i,'t_wall',c,r) for i,(c,r) in enumerate([(14,15),(14,14),(15,14)])]
        self.rejects(wall_in,'cannot be reached')

    def test_the_catalog_enforces_the_roles_table(self):
        self.assertEqual(ROLES['floor']['blocks'],False);self.assertEqual(ROLES['wall']['blocks'],True);self.assertIsNone(ROLES['structure']['blocks'])

    def test_older_schemas_still_validate(self):
        from world_test_support import manifest
        self.assertEqual(validate_manifest(manifest())[0]['schema'],'meadow-world-v1')

class ExportedCatalogs(unittest.TestCase):
    """The catalogs the Blender exporter wrote must pass the same role rules the backend enforces."""
    def test_every_exported_piece_validates_in_its_own_world(self):
        root=Path(__file__).resolve().parents[2]/'TScanViewer/Assets/Resources/Meadow/kit'
        files=sorted(glob.glob(str(root/'catalog_*.json')))
        if not files:self.skipTest('no exported catalogs present')
        pieces=[]
        for f in files:
            with open(f,encoding='utf-8') as handle:pieces+=json.load(handle)['pieces']
        self.assertGreater(len(pieces),50)
        floor=next(p for p in pieces if p['role']=='floor')
        for p in pieces:
            if p['role']=='actor':continue
            m=built();m['catalog']=[piece(floor['id'],floor['name'],'floor',False)];m['floors']=[floor['id']]*225;m['obstacles']=[];m['props']=[]
            if p['role']!='floor':
                m['catalog'].append(piece(p['id'],p['name'],p['role'],p['blocks']))
                (m['obstacles'] if p['blocks'] else m['props']).append(placement('x',p['id'],3,3))
            validate_manifest(m)

class BuiltWorldInTheLoop(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.world=GridWorld(Path(self.tmp.name)/'world.json');self.world.register_world('test',built());self.world.reset()
    def tearDown(self):self.tmp.cleanup()

    def test_observation_names_pieces_and_marks_hazards(self):
        s=self.world.observe()
        names={o['id']:(o['name'],o['role']) for o in s['visible_obstacles']};self.assertEqual(names['w1'],('Test wall','wall'));self.assertEqual(names['d1'],('Test door','structure'))
        self.assertEqual([h['name'] for h in s['visible_hazards']],['Test spike trap'])
        self.assertEqual(s['surroundings']['east'],dict(terrain='obstacle',target=None,feature='Test wall'))
        self.assertEqual(s['surroundings']['south']['terrain'],'hazard');self.assertEqual(s['surroundings']['south']['feature'],'Test spike trap')
        self.assertEqual(s['surroundings']['west']['feature'],'Test barrel')

    def test_movement_respects_classes(self):
        s=self.world.observe();blocked=self.world.nominate('move_east',{},'t1',s['observation_id'],'c1');self.assertEqual(blocked['outcome'],'blocked_obstacle')
        self.world.acknowledge('test',blocked['action_id'],s['session_id'])
        s=self.world.observe();onto=self.world.nominate('move_south',{},'t2',s['observation_id'],'c2');self.assertEqual(onto['outcome'],'moved');self.assertEqual(onto['position_after'],[8,7])
        self.world.acknowledge('test',onto['action_id'],s['session_id']);self.assertEqual(self.world.observe()['hazard_here'],'h1')
        s=self.world.observe();through=self.world.nominate('move_north',{},'t3',s['observation_id'],'c3');self.assertEqual(through['outcome'],'moved');self.world.acknowledge('test',through['action_id'],s['session_id'])
        s=self.world.observe();door=self.world.nominate('move_north',{},'t4',s['observation_id'],'c4');self.assertEqual(door['outcome'],'blocked_obstacle')   # the closed door at (8,9)

    def test_the_model_text_groups_pieces_by_curated_name_and_never_shows_prototype_ids(self):
        text=coordinate_world(self.world.observe())
        self.assertIn('OBSTACLES / measured cells that cannot be entered',text);self.assertIn('{"name":"Test wall","role":"wall","cells":[[9,8],[9,9]]}',text)
        self.assertIn('HAZARDS / measured cells you may enter',text);self.assertIn('{"name":"Test spike trap","cells":[[8,7]]}',text)
        self.assertIn('! hazard',text);self.assertNotIn('t_wall',text);self.assertNotIn('t_spikes',text);self.assertNotIn('Test flowers',text)   # decor is cosmetic, not model context
        map_rows=[l for l in text.splitlines() if l.startswith('07 ')];self.assertIn('!',map_rows[0])

if __name__=='__main__':unittest.main()
